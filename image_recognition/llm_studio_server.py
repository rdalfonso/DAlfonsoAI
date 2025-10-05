from openai import OpenAI
import os
import json
import base64

# Must match LM Studio model name
model = "google/gemma-3n-e4b"  

# Connect to LM Studio's local API
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

# Directory with your images
images_dir = "./images"

# Create a directory for renamed images
renamed_dir = "./images_renamed"
os.makedirs(renamed_dir, exist_ok=True)

# Loop over all supported image files
for filename in os.listdir(images_dir):
    if filename.lower().endswith(".jpg"):
        print(f"filename: {filename}")

        # Path to your image
        image_path = os.path.join(images_dir, filename)
        print(f"image_path: {image_path}")

        # Read and base64-encode the image
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

            response = client.chat.completions.create(
                model=model,
                messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": (
                                "What's on this image? Return JSON with two fields: "
                                "`description` (a short description), and "
                                "`name` (a few words with no spaces)."
                                )},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_b64}"
                                    },
                                },
                            ],
                        }
                    ],
                response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "image_description",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "name": {"type": "string"}
                                },
                                "required": ["description", "name"]
                            }
                        }
                    }
        )


        # handle json structured output response.
        raw = response.choices[0].message.content
        try:
            result = json.loads(raw)

            # Set values from response
            description = result.get("description", "")
            name = result.get("name", "")

            # Always use .jpg for new name
            new_filename = f"{name.replace(' ', '_').lower()}.jpg"
            new_path = os.path.join(images_dir, new_filename)
            os.rename(image_path, new_path)

            os.makedirs(renamed_dir, exist_ok=True)
            final_path = os.path.join(renamed_dir, new_filename)
            os.rename(new_path, final_path)

            # Print result
            print(f"Renamed: {filename} → {new_filename}")
            print(f"Description: {description}")
            print(f"Name: {name.lower().replace(' ', '_')}")
        except json.JSONDecodeError:
            print(f"Could not parse JSON: {raw}")