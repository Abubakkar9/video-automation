from dotenv import dotenv_values
from openai import OpenAI
import json

config = dotenv_values(".env")  

client = OpenAI(
    # This is the default and can be omitted
    api_key=config.get("OPENAI_API_KEY"),
)

def generate_images(prompt, n, size):
    images = []
    try:       
        # Generate the image using OpenAI's image generation API
        response = client.images.generate(
            prompt=prompt,
            size=size,
            n=n
        )
        print(response)
    except Exception as e:
            print(f"Error generating images: {str(e)}")

    return images


def generate_variation_images(n, size, image):
    images = []
    try:       
        # Generate the image using OpenAI's image generation API
        response = client.images.create_variation(
            image=image,
            size=size,
            n=n
        )
        return response
    except Exception as e:
            print(f"Error generating variation images: {str(e)}")

    return images