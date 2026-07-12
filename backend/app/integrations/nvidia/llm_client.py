from openai import AsyncOpenAI

NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"


async def create_chat_completion(client: AsyncOpenAI, prompt: str):
    return await client.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=False,
    )
