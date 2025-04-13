from fastapi import FastAPI
from pydantic import BaseModel
import openai
import requests

app = FastAPI()
openai.api_key = "YOUR_OPENAI_API_KEY"
ORS_API_KEY = "YOUR_ORS_API_KEY"

class PromptRequest(BaseModel):
    prompt: str
    start: list
    end: list

@app.post("/generate-route")
async def generate_route(data: PromptRequest):
    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're an assistant that helps generate cycling route preferences."},
            {"role": "user", "content": f"Extract preferences from: '{data.prompt}'"}
        ]
    )

    parsed = gpt_response["choices"][0]["message"]["content"]

    response = requests.post(
        "https://api.openrouteservice.org/v2/directions/cycling-regular",
        headers={"Authorization": ORS_API_KEY, "Content-Type": "application/json"},
        json={"coordinates": [data.start, data.end]}
    )

    return response.json()
