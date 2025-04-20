from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os
import logging
import openai

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# ✅ Get API keys from environment
openai_api_key = "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"
ORS_API_KEY = os.getenv("ORS_API_KEY")

# ✅ Debug: Log the OpenAI key to check if it's being passed
logging.info(f"OPENAI_API_KEY detected: {openai_api_key}")

openai.api_key = openai_api_key

class PromptRequest(BaseModel):
    prompt: str
    start: list
    end: list

@app.post("/generate-route")
async def generate_route(data: PromptRequest, request: Request):
    try:
        logging.info(f"Prompt received: {data.prompt}")

        # ✅ OpenAI v0.28.x style
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that helps generate cycling route preferences."},
                {"role": "user", "content": f"Extract preferences from: \"{data.prompt}\""}
            ]
        )
        parsed_text = gpt_response.choices[0].message.content
        logging.info(f"AI interpreted prompt as: {parsed_text}")

        # ✅ Call OpenRouteService
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
