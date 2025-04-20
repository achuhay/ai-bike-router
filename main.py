from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os
import logging
from openai import OpenAI  # ✅ OpenAI v1 client

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ORS_API_KEY = os.getenv("ORS_API_KEY")

class PromptRequest(BaseModel):
    prompt: str
    start: list
    end: list

@app.post("/generate-route")
async def generate_route(data: PromptRequest, request: Request):
    try:
        logging.info(f"Prompt received: {data.prompt}")

        # ✅ OpenAI v1 SDK usage
        gpt_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're an assistant that helps generate cycling route preferences."},
                {"role": "user", "content": f"Extract preferences from: '{data.prompt}'"}
            ]
        )
        parsed_text = gpt_response.choices[0].message.content
        logging.info(f"AI interpreted prompt as: {parsed_text}")

        # Send request to ORS
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
