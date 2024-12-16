from moviepy import ImageSequenceClip, AudioFileClip
from PIL import Image, ImageDraw
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

# Helper function to download images (mock implementation)
def download_images(image_urls):
    # Mock function: Assume `image_urls` are already local file paths
    return image_urls


# Example usage
image_urls = ["temp_images/image_0.jpg", "temp_images/image_1.jpg", "temp_images/image_2.jpg", "temp_images/image_0.jpg"]
audio_file = "audios/CwhRBWXzGAHq8TQ4Fs17_Ahoy, mateys! Are yo.mp3"
output_file = "output_video.mp4"

create_video_from_images_and_audio(image_urls, audio_file, output_file)
