import os
import base64
import json
from openai import OpenAI

# Connect to Ollama locally
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # dummy value, required by SDK
)

# Directory with your images
images_dir = "./images/process"

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

        # Construct OpenAI-style request with image input
        response = client.chat.completions.create(
            model="gemma3:12b-it-qat",  # or gemma3 if it supports vision
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": (
                            "What's on this image? Return JSON with two fields: "
                            "`description` (a detailed description), and "
                            "`caption` (a short 4-5 word snake_case caption)."
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
            response_format={"type": "json_object"},  # Force structured JSON output
        )

        # Parse JSON response
        raw = response.choices[0].message.content
        try:
            result = json.loads(raw)

            description = result.get("description", "")
            caption = result.get("caption", "")

            # Always use .jpg for new name
            new_filename = f"{caption.replace(' ', '_').lower()}.jpg"
            new_path = os.path.join(images_dir, new_filename)

            os.rename(image_path, new_path)

            # Print result
            print(f"Renamed: {filename} → {new_filename}")
            print(f"Description: {description}")
            print(f"Caption: {caption}\n")
        except json.JSONDecodeError:
            print(f"Could not parse JSON for {filename}: {raw}\n")