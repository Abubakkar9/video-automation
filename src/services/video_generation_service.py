from src.services.image_generation_service import generate_variation_images
from src.services.voice_generation_service import generate_audio
from moviepy import ImageSequenceClip, AudioFileClip, concatenate_videoclips
from pydub import AudioSegment
import os
import requests
import base64
from PIL import Image, ImageDraw
import os

def generate_videos_in_bulk(num_of_images, base_image, scripts, voice_actors, divider=3):
    
    base_image_bytes = None
    # Open the saved base image file in binary read mode ('rb')
    with open(base_image, 'rb') as file:
       base_image_bytes = file.read()  # Reads the entire file and returns it as byte

    images = generate_variation_images(num_of_images, '1024x1024', base_image_bytes)
    videos_map = {}
    images_index = 0
    i = 0
    for voice_actor_id in voice_actors:
        videos_map[voice_actor_id] = []
        for script in scripts:
            temp_images = []
            start = i % len(images.data)  # Start index
            end = (start + divider) % len(images.data)  # End index (wrap around using modulo)
            if end > start:  # Normal slice
                temp_images = images.data[start:end]
            else:  # Wrap-around slice
                temp_images = images.data[start:] + images.data[:end]

            temp_images = [image.url for image in temp_images]
            images_index = images_index + divider
            audio_base64 = generate_audio(script, voice_actor_id)
            audio_data = base64.b64decode(audio_base64)

            with open("audios/" + voice_actor_id + '_' + script[0:20] + ".mp3", "wb") as f:
                f.write(audio_data)

            output_file = 'static/videos/' + voice_actor_id + '_' + script[0:20] + ".mp4"
            videos_map[voice_actor_id].append( 
                create_video_from_images_and_audio(
                    temp_images,
                    "audios/" + voice_actor_id + '_' + script[0:20] + ".mp3",
                    output_file
                )
            )
            i+=1

    return videos_map

def download_images(image_urls, download_folder="temp_images"):
    """
    Downloads images from a list of URLs and saves them to a local folder.

    Args:
        image_urls (list): List of image URLs to download.
        download_folder (str): Path to the folder where images will be saved.

    Returns:
        list: List of file paths to the downloaded images.
    """
    os.makedirs(download_folder, exist_ok=True)  # Create the folder if it doesn't exist
    downloaded_files = []
    
    for i, url in enumerate(image_urls):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(download_folder, f"image_{i}.jpg")
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            downloaded_files.append(file_path)
        else:
            print(f"Failed to download image from {url}")
    
    return downloaded_files

import numpy as np  # Import NumPy

def create_video_from_images_and_audio(image_urls, audio_file, output_file, click_effect_duration=0.2):
    """
    Creates a video with a main image display and a carousel of thumbnails below,
    simulating a mouse click effect on the active thumbnail, with the mouse pointer in the middle of the click effect.

    Args:
        image_urls (list): List of image file paths or URLs in the correct order.
        audio_file (str): Path to the audio file.
        output_file (str): Path where the output video will be saved.
        click_effect_duration (float): Duration of the click effect in seconds.
    """
    # Step 1: Download images if they are URLs
    images = download_images(image_urls)  # Replace this with your own `download_images` implementation.
    
    # Insert intro and outro images
    intro_image = 'images/intro.png'
    outro_image = 'images/outro.png'
    images.insert(0, intro_image)  # Add intro at the beginning
    images.append(outro_image)  # Add outro at the end

    # Resize all images to 800x600 to ensure consistency
    def resize_image(image_path, size=(800, 600)):
        image = Image.open(image_path)
        image = image.convert("RGB")  # Ensure all images are in RGB mode (no alpha channel)
        return image.resize(size)

    # Step 2: Create frames with the main image and carousel
    frames = []
    fps = int(1 / click_effect_duration)  # Frames per second for the click effect
    
    mouse_pointer_size = (20, 20)  # Size of the simulated mouse pointer

    # Load the audio and calculate total length
    audio = AudioFileClip(audio_file)
    total_audio_length = audio.duration

    # Calculate the duration for each image (excluding intro and outro)
    num_images = len(images) - 2  # Excluding intro and outro images
    image_duration = total_audio_length / num_images

    # ** Add frames for the intro image for 2 seconds **
    intro_image_resized = resize_image(intro_image)
    intro_frames = [np.array(intro_image_resized)] * (2 * fps)  # Convert PIL image to NumPy array
    frames.extend(intro_frames)  # Ensure intro frames are added at the start

    # Only add frames for the images excluding the intro and outro
    for i, main_image_path in enumerate(images[1:-1]):  # Skip the intro and outro images in the carousel
        # Calculate the number of frames for the current image
        num_frames_for_image = int(fps * image_duration)  # Total frames for the current image
        
        # Generate frames for the current image
        for _ in range(num_frames_for_image):
            # Open the main image
            main_image = resize_image(main_image_path)  # Resize to a standard size

            # Create a blank canvas for the video frame (size: 800x600)
            canvas = Image.new("RGB", (800, 600), "white")  # Adjust height for carousel
            canvas.paste(main_image, (0, 0))  # Place the main image at the top

            # Create the carousel below the main image (no intro and outro images here)
            thumbnail_size = (100, 75)
            x_offset = 10
            for j, thumbnail_path in enumerate(images[1:-1]):  # Skip intro and outro images in the carousel
                thumbnail = resize_image(thumbnail_path, size=thumbnail_size)

                if i == j:  # Active thumbnail
                    draw = ImageDraw.Draw(thumbnail)

                    # Simulate the click effect with a shrinking circle
                    if _ < fps // 2:
                        # Draw a shrinking circle around the mouse pointer
                        radius = 20 - _ * 2  # Shrink over time
                        center_x, center_y = thumbnail_size[0] // 2, thumbnail_size[1] // 2
                        draw.ellipse(
                            [(center_x - radius, center_y - radius),
                             (center_x + radius, center_y + radius)],
                            outline="blue", width=3
                        )

                    # Add a "mouse pointer" graphic in the center of the circle
                    pointer = Image.new("RGBA", mouse_pointer_size, (255, 255, 255, 0))  # Transparent pointer
                    pointer_draw = ImageDraw.Draw(pointer)
                    pointer_draw.polygon([(0, 0), (10, 5), (5, 10)], fill="black")  # Triangle for pointer

                    # Position the pointer in the middle of the thumbnail
                    pointer_x = thumbnail_size[0] // 2 - mouse_pointer_size[0] // 2
                    pointer_y = thumbnail_size[1] // 2 - mouse_pointer_size[1] // 2
                    thumbnail.paste(pointer, (pointer_x, pointer_y), pointer)  # Place the pointer on the thumbnail

                    # Final red border for the active thumbnail
                    draw.rectangle([(0, 0), thumbnail.size], outline="red", width=5)

                canvas.paste(thumbnail, (x_offset, 520))  # Position the thumbnail below the main image
                x_offset += 110  # Add spacing between thumbnails

            # Convert the frame to NumPy array and add to frames
            frame_array = np.array(canvas)  # Convert PIL image to NumPy array
            frames.append(frame_array)  # Add to frames list

    # ** Add frames for the outro image for 2 seconds **
    outro_image_resized = resize_image(outro_image)
    outro_frames = [np.array(outro_image_resized)] * (2 * fps)  # Convert PIL image to NumPy array
    frames.extend(outro_frames)  # Ensure outro frames are added at the end

    # Step 3: Check if all frames have the same size
    frame_size = frames[0].shape
    for frame in frames:
        if frame.shape != frame_size:
            print(f"Error: Frame size mismatch. Expected {frame_size}, found {frame.shape}")
            return

    # Step 4: Create a video clip from the generated frames
    video_clip = ImageSequenceClip(frames, fps=fps)

    # Step 5: Load and attach the audio file
    video_clip.audio = audio

    # Step 6: Write the final video to a file
    video_clip.write_videofile(output_file, codec="libx264", audio=True)

    return output_file