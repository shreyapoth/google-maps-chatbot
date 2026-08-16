import asyncio
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from langgraph.errors import GraphRecursionError

from app.api.chat import chat as chat_module
from app.bootstrap import get_agent
from app.main import app

THREAD_ID = "11111111-1111-4111-8111-111111111111"

CHAT_REQUEST = {
    "message": "find me tacos nearby",
    "location": {"latitude": 30.27, "longitude": -97.74},
    "thread_id": THREAD_ID,
}


def _fake_agent() -> AsyncMock:
    agent = AsyncMock()
    app.dependency_overrides[get_agent] = lambda: agent
    return agent


def test_chat_endpoint_returns_the_final_agent_message():
    agent = _fake_agent()
    agent.ainvoke.return_value = {
        "messages": [
            AIMessage(content="Looking for tacos..."),
            AIMessage(content="Torchy's is 4 minutes away."),
        ]
    }

    try:
        response = TestClient(app).post("/chat", json=CHAT_REQUEST)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "reply": "Torchy's is 4 minutes away.",
        "thread_id": THREAD_ID,
    }


def test_chat_endpoint_gives_the_agent_the_users_coordinates():
    agent = _fake_agent()
    agent.ainvoke.return_value = {"messages": [AIMessage(content="ok")]}

    try:
        TestClient(app).post("/chat", json=CHAT_REQUEST)
    finally:
        app.dependency_overrides.clear()

    state = agent.ainvoke.await_args.args[0]
    [user_message] = state["messages"]

    assert user_message.content == (
        "My current location is lat 30.27, lng -97.74.\nfind me tacos nearby"
    )


def test_chat_endpoint_reports_an_empty_agent_reply():
    agent = _fake_agent()
    agent.ainvoke.return_value = {"messages": []}

    try:
        response = TestClient(app).post("/chat", json=CHAT_REQUEST)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "AGENT_EMPTY_RESPONSE"


def test_chat_endpoint_caps_the_agents_step_count():
    agent = _fake_agent()
    agent.ainvoke.return_value = {"messages": [AIMessage(content="ok")]}

    try:
        TestClient(app).post("/chat", json=CHAT_REQUEST)
    finally:
        app.dependency_overrides.clear()

    config = agent.ainvoke.await_args.kwargs["config"]
    assert config["recursion_limit"] == chat_module.AGENT_RECURSION_LIMIT


def test_chat_endpoint_tags_the_run_with_the_request_id():
    agent = _fake_agent()
    agent.ainvoke.return_value = {"messages": [AIMessage(content="ok")]}

    try:
        response = TestClient(app).post("/chat", json=CHAT_REQUEST)
    finally:
        app.dependency_overrides.clear()

    config = agent.ainvoke.await_args.kwargs["config"]
    assert config["run_name"] == "chat"
    assert config["tags"] == ["chat"]
    assert config["configurable"]["thread_id"] == THREAD_ID
    assert config["metadata"]["thread_id"] == THREAD_ID
    assert config["metadata"]["request_id"] == response.headers["X-Request-ID"]


def test_chat_endpoint_reports_a_looping_agent():
    agent = _fake_agent()
    agent.ainvoke.side_effect = GraphRecursionError("Recursion limit of 15 reached")

    try:
        response = TestClient(app).post("/chat", json=CHAT_REQUEST)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "AGENT_STEP_LIMIT"


def test_chat_endpoint_gives_up_on_a_stalled_agent(monkeypatch):
    monkeypatch.setattr(chat_module, "AGENT_TIMEOUT_SECONDS", 0.01)
    agent = _fake_agent()

    async def never_answers(*args, **kwargs):
        await asyncio.sleep(5)

    agent.ainvoke.side_effect = never_answers

    try:
        response = TestClient(app).post("/chat", json=CHAT_REQUEST)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 504
    assert response.json()["detail"]["code"] == "AGENT_TIMEOUT"


def test_chat_endpoint_rejects_a_blank_message():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "message": "   ",
                "location": {"latitude": 30.27, "longitude": -97.74},
                "thread_id": THREAD_ID,
            },
        )

    assert response.status_code == 422


def test_chat_endpoint_requires_a_location():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"message": "find me tacos", "thread_id": THREAD_ID},
        )

    assert response.status_code == 422


def test_chat_endpoint_requires_a_thread_id():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "message": "find me tacos",
                "location": {"latitude": 30.27, "longitude": -97.74},
            },
        )

    assert response.status_code == 422
