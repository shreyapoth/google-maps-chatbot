from openai import OpenAI
from app.core.config import settings

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"


def get_nvidia_client() -> OpenAI:
    if not settings.nvidia_api_key:
        raise RuntimeError("NVIDIA_API_KEY is required")

    return OpenAI(base_url=NVIDIA_BASE_URL, api_key=settings.nvidia_api_key)


def create_chat_completion(prompt: str):
    client = get_nvidia_client()
    return client.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=False,
    )