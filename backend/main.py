# Main imports
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from decouple import config
import openai
import re
from io import BytesIO

# To time functionalities
import time
import os

# Custom functions import
from functions.requests import audio_to_text, get_response_choice, store_conversation, rank_and_regenerate
from functions.database import store_messages, reset_messages
from functions.text_to_speech import convert_text_to_speech

# Initiate App
app = FastAPI()

# Mount a static file route
app.mount("/static", StaticFiles(directory="static"), name="static") # For recordings

# CORS - Origins (Domains to accepts) (Add front end local host url here later)
# 192.168.18.13
origins = [
    "http://172.20.10.6:8081",
    "http://192.168.18.13:8081",
    "http://localhost:8000",
]

# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.get("/")
async def root():
    return {"message": "Hellow World"}

# Checking of health
@app.get("/health")
async def check_health():
    return {"message": "Healthy!"}

@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):

    safe_filename = file.filename.replace(" ", "_")
    print(safe_filename)

    try:
        # Save file from Frontend
        with open(safe_filename, "wb") as buffer:
            buffer.write(await file.read())

        # Read the saved file and process it
        with open(safe_filename, "rb") as audio_input:
            text = audio_to_text(audio_input)

        # Ensure text was decoded
        if not text:
            return JSONResponse(status_code=400, content={"message": "Failed to decode audio"})

        print("Text converted is:", text)
        return {"message": "File processed successfully", "text": text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

# Transcribe audio and get chat gpt response
@app.post("/post-audio-response/")
async def post_audio_response(file: UploadFile = File(...), mute: str = Form(...), normal: str = Form(...), final_response: str = Form(...)):
    
    safe_filename = "recordings/" + file.filename.replace(" ", "_")
    print(safe_filename)

    try:
        start_audio_to_text = time.time()
        # Save file from Frontend
        with open(safe_filename, "wb") as buffer:
            buffer.write(await file.read())

        # Read the saved file and process it
        with open(safe_filename, "rb") as audio_input:
            text = audio_to_text(audio_input)

        # Ensure text was decoded
        if not text:
            return JSONResponse(status_code=400, content={"message": "Failed to decode audio"})
        audio_to_text_time = time.time() - start_audio_to_text
        print(f"\nAudio to text time: {audio_to_text_time} seconds\n")

        # Get ChatGPT Response
        start_get_response_choice = time.time()
        user_message_and_response = get_response_choice(mute, normal, final_response, text, search = True)
        get_response_choice_time = time.time() - start_get_response_choice

        response_choices = user_message_and_response[0]
        #print("response_choices:", response_choices)
        print(f"\nGet response choice time: {get_response_choice_time} seconds\n")

        responses = split_and_clean_responses(response_choices)

        #responses = response_choices.split('@')
                
        # if(len(responses) < 3):
        #     responses = response_choices.split('\n')

        if(len(responses) > 3):
            responses = responses[:3]

        print(responses)

        # Guard: Ensure there was a response from chatgpt
        if not user_message_and_response:
            return HTTPException(status_code = 400, detail = "Failed to get chatgpt response")

        # Store messages into json file for history of top 5
        store_messages(user_message_and_response[1], response_choices)

        # Total time
        total_process_time = time.time() - start_audio_to_text
        print(f"\nTotal process time: {total_process_time} seconds\n")
               

        return {"message": "File processed successfully", "transcription": text, "response_choices": responses}

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
    
    
    

    # # Convert final response to audio
    # audio_output = convert_text_to_speech(final_response)

    # # Guard: Ensure text converted to audio
    # if not audio_output:
    #     return HTTPException(status_code = 400, detail = "Failed to convert text to audio")

    # # Create a generator that yield data
    # def iterfile():
    #     yield audio_output

    # # Return and save audio file:
    # #return StreamingResponse(iterfile(), media_type="audio/mpeg")
    # return StreamingResponse(iterfile(), media_type="application/octet-stream")

# Text To Speech Response
@app.post("/text-to-speech/")
async def text_to_speech(response: str = Form(...)):
    audio_output = convert_text_to_speech(response)
    if not audio_output:
        raise HTTPException(status_code=500, detail="Failed to convert text to speech")
    
    audio_file_path = "C:\\Roydon\\Github\\FYP_Application\\MuteCompanion\\backend\\static\\response.mp3"
    with open(audio_file_path, "wb") as f:
        f.write(audio_output)

    return {"message": "Audio saved successfully"}


# Store conversation (Response selected and normal persons prompts/query)
@app.post("/store-response/")
async def store_response(mute: str = Form(...), normal: str = Form(...), query: str = Form(...), response: str = Form(...)):
    filename = f"C:\\Roydon\\Github\\FYP_Application\\MuteCompanion\\MuteApp\\assets\\mockdata\\{mute}\\{normal}.json"
    store_conversation(filename, mute, normal, query, response)
    return {"message": "Conversation stored successfully"}

# Reset messages or conversation to start a new conversation
@app.get("/reset")
async def reset():
    reset_messages()
    return {"message": "Conversation has been resetted"}


# Refresh and regenerate responses
@app.post("/regenerate-responses/")
async def regenerate_responses(mute: str = Form(...), normal: str = Form(...), final_response: str = Form(...), text: str = Form(...)):

    # Remove history to regenerate responses
    reset_messages()

    # Get ChatGPT Response
    start_get_response_choice = time.time()
    user_message_and_response = get_response_choice(mute, normal, final_response, text, search = True)
    get_response_choice_time = time.time() - start_get_response_choice

    response_choices = user_message_and_response[0]
    #print("response_choices:", response_choices)
    print(f"Regenerate response choice time: {get_response_choice_time} seconds")

    responses = split_and_clean_responses(response_choices)

    #responses = response_choices.split('@')
            
    # if(len(responses) < 3):
    #     responses = response_choices.split('\n')

    if(len(responses) > 3):
        responses = responses[:3]

    print(responses)

    # Guard: Ensure there was a response from chatgpt
    if not user_message_and_response:
        return HTTPException(status_code = 400, detail = "Failed to get chatgpt response")

    # Store messages
    store_messages(user_message_and_response[1], response_choices)

    return {"message": "Responses regenerated successfully", "transcription": text, "response_choices": responses}


# Refresh an individual response through scoring
@app.post("/rank-responses/")
async def rank_responses(mute: str = Form(...), normal: str = Form(...), responses: list = Form(...), query: str = Form(...), scores: list = Form(...), badResponse: str = Form(...)):
    newResponse = rank_and_regenerate(mute, normal, responses, query, scores, badResponse)

    return {"message": "Response ranked and regenerated successfully", "new_response": newResponse}


#--------------------------------------------- HELPER FUNCTIONS ---------------------------------------------

# Helper functions:
def split_and_clean_responses(input_string):
    # Split the string using the pattern "Response X:"
    responses = re.split(r'Response \d+:', input_string)
    
    # Remove the first empty item and strip whitespace and new lines from each response
    cleaned_responses = [response.strip() for response in responses if response]

    return cleaned_responses