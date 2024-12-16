from elevenlabs import save, play
from elevenlabs.client import ElevenLabs
from dotenv import dotenv_values

config = dotenv_values(".env")  

# Initialize the client
client = ElevenLabs(
    api_key=config.get("ELEVENLABS_API_KEY"),
)

def get_model():
    try:
        models = client.models.get_all()
        return models[0]
    except Exception as e:
        print('Unable to get the model')
        return None
            
def get_all_voice_actors():
    response = []
    try:
        voices = client.voices.get_all()
        for voice in voices.voices:
            response.append(
                {
                    'voice_id' : voice.voice_id,
                    'name' : voice.name
                }
            )
        return response
    except Exception as e:
        return None

def generate_audio(prompt, voice_actor_id):
    try:
        print (prompt, voice_actor_id)
        # Generate the audio
        audio = client.text_to_speech.convert_with_timestamps(
            text=prompt,
            voice_id=voice_actor_id,
            model_id=get_model().model_id,
            output_format="mp3_44100_128",
        )
        # audio = client.generate(
        #     text=prompt,
        #     voice=voice_actor_id,
        #     model=get_model().model_id
        # )
        #play(audio)
        return audio['audio_base64']
    except Exception as e:
        print(e)
        return None
    
