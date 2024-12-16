idea = """
Title: "I Survived 24 Hours Living Like a Pirate!"

Concept:
    * Dress up as a pirate for a day and live out pirate-themed challenges.
    * Build a mini “ship” or raft, decorate a room to look like a pirate’s cabin, and eat only pirate-inspired food (think hardtack and rum-themed mocktails).
    * Create a treasure hunt with a map, solve riddles, and dig for a hidden treasure.
    * Add humor by speaking in pirate slang the entire time and interacting with “crew members” (friends or props).
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from src.services.voice_generation_service import get_all_voice_actors, generate_audio
from src.services.content_generation_service import generate_marketing_scripts
from src.services.video_generation_service import generate_videos_in_bulk
import json
import os
# Create a Flask app instance
app = Flask(__name__)


@app.route('/')
def home():
    # Render the index.html template
    voice_actors = get_all_voice_actors()
    print(voice_actors)
    return render_template('index.html', voice_actors=voice_actors)


@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory('static/videos', filename)

@app.route('/generate-scripts', methods=['POST'])
def generate_scripts():
    # Get the data from the request
    video_idea = request.form.get('video_idea')
    num_scripts = int(request.form.get('num_scripts'))

    scripts = generate_marketing_scripts(video_idea, num_scripts)
    print(scripts)
    
    return scripts

@app.route('/generate-videos', methods=['POST'])
def generate_videos():
    # Get the data from the request
    num_of_images = int(request.form.get('num_of_images'))
    scripts = json.loads(request.form.get('scripts'))
    
    # Parse the voice_actors from JSON string (sent from client as a JSON string)
    voice_actors = json.loads(request.form.get('voice_actors'))
    
    # Handle the uploaded file (base image)
    base_image = request.files.get('base_image')
    
    # Check if base image is uploaded
    if base_image:
        # Save or process the file as needed (e.g., save it temporarily)
        base_image_filename = os.path.join('uploads', base_image.filename)
        base_image.save(base_image_filename)  # Save the file to the 'uploads' directory
    else:
        return {"error": "No base image uploaded"}, 400
    
    # Call your video generation logic here
    videos = generate_videos_in_bulk(num_of_images, base_image_filename, scripts, voice_actors)
    
    # Return the generated videos (you can return URLs, paths, or any relevant data)
    return {"videos": videos}


if __name__ == '__main__':
    # Run the application
    app.run(debug=True)
