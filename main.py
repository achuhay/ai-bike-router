from fastapi import FastAPI
from pydantic import BaseModel
import openai
import requests
import os

app = FastAPI()

# Get keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
ORS_API_KEY = os.getenv("ORS_API_KEY")

class PromptRequest(BaseModel):
    prompt: str
    start: list
    end: list

@app.post("/generate-route")
async def generate_route(data: PromptRequest):
    # Step 1: Ask AI to interpret the prompt (just logging for now)
    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're an assistant that helps generate cycling route preferences."},
            {"role": "user", "content": f"Extract preferences from: '{data.prompt}'"}
        ]
    )
    parsed_text = gpt_response["choices"][0]["message"]["content"]
    print("AI said:", parsed_text)

    # Step 2: Use ORS to get the route
    ors_response = requests.post(
        "https://api.openrouteservice.org/v2/directions/cycling-regular",
        headers={
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "coordinates": [data.start, data.end],
            "instructions": True,
            "elevation": True
        }
    )

    # Step 3: Return the full route response
    return ors_response.json()
