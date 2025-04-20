from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os
import logging
import openai

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# ✅ Old style OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")
ORS_API_KEY = os.getenv("ORS_API_KEY")

class PromptRequest(BaseModel):
    prompt: str
    start: list
    end: list

@app.post("/generate-route")
async def generate_route(data: PromptRequest, request: Request):
    try:
        logging.info(f"Prompt received: {data.prompt}")

        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that helps generate cycling route preferences."},
                {"role": "user", "content": f"Extract preferences from: \"{data.prompt}\""}
            ]
        )
        parsed_text = gpt_response.choices[0].message["content"]
        logging.info(f"AI interpreted prompt as: {parsed_text}")

        # OpenRouteService call
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

        logging.info(f"ORS response: {ors_response.text}")
        return ors_response.json()

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return {"error": "Internal server error", "details": str(e)}
