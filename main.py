from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os
import logging
import openai  # ✅ OpenAI v1.x import

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# ✅ Set API keys from environment
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

        # ✅ OpenAI v1.x chat completion call
        gpt_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "
