import pytest

from app.integrations.nvidia.llm_client import NVIDIA_MODEL
from app.integrations.nvidia.llm_client import create_chat_completion


class FakeCompletions:
    def __init__(self):
        self.kwargs = None

    async def create(self, **kwargs):
        self.kwargs = kwargs
        return {"id": "completion-1"}


class FakeChat:
    def __init__(self):
        self.completions = FakeCompletions()


class FakeAsyncOpenAI:
    def __init__(self):
        self.chat = FakeChat()


@pytest.mark.asyncio
async def test_create_chat_completion_uses_injected_async_client():
    client = FakeAsyncOpenAI()

    result = await create_chat_completion(client, "find a route")

    assert result == {"id": "completion-1"}
    assert client.chat.completions.kwargs == {
        "model": NVIDIA_MODEL,
        "messages": [{"role": "user", "content": "find a route"}],
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 1024,
        "stream": False,
    }
