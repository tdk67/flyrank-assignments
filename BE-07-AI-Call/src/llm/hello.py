import os
from dotenv import load_dotenv
from openai import OpenAI

from src.config import config

base_url = config.llm_base_url
api_key = config.llm_api_key
model = config.llm_model

print(f"Connecting to provider at: {base_url} with model: {model}")

client = OpenAI(base_url=base_url, api_key=api_key)

try:
    res = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Reply with exactly the word: ready"}],
        temperature=0.0,
        timeout=config.timeout_seconds,
    )
    output = res.choices[0].message.content.strip()
    print(f"Model response: {output}")
except Exception as e:
    print(f"Error connecting to model: {e}")
