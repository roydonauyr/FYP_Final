import requests
from decouple import config

ELEVEN_LABS_API_KEY = config("ELEVEN_LABS_API_KEY")

# Voice ids, person
# Rachel: 21m00Tcm4TlvDq8ikWAM (Young, female, naration)
# Drew: 29vD33N1CtxCmqQRPOHJ (Middle aged, male)
# Clide: 2EiwWnXFnvU5JabPnv8n (Middle aged, male, war veteran)
# Paul: 5Q0t7uMcjvnagumLfvZi (Middle aged, male, ground reporter)


# Convert Text To Speech
def convert_text_to_speech(message):
    data = {
        "text": message,
        "voice_settings":{
            "stability": 0, # Adjusts the amount of emotion in the voice,
            "similarity_boost": 0,
        }
    }

    rachel_bot_id = "21m00Tcm4TlvDq8ikWAM"

    # Construct headers:
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY,
        "accept": "audio/mpeg"
    }

    # Construct api endpoints.
    endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{rachel_bot_id}"

    # Send request
    try:
        response = requests.post(endpoint, json=data, headers=headers)
    except Exception as e:
        return
    
    # Handle Response
    if response.status_code == 200:
        return response.content
    else:
        return