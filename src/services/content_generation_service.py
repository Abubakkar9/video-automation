from dotenv import dotenv_values
from openai import OpenAI
import json

config = dotenv_values(".env")  

client = OpenAI(
    # This is the default and can be omitted
    api_key=config.get("OPENAI_API_KEY"),
)

def generate_marketing_scripts(idea, n):
    scripts = []
    try:
        # Generating marketing scripts
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Place model parameter first for clarity
            messages=[
                {
                    "role": "user",
                    "content": f"""Please generate {n} marketing scripts for the following story:
                    {idea}
                    Return the response as {{"scripts": ["script1 content", "script2 content", ...]}}.
                    Note: Just include script text. Do not include anything else. Even not numbering.
                    """,
                }
            ],
        )
        scripts = json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Error generating scripts: {str(e)}")
    
    return scripts