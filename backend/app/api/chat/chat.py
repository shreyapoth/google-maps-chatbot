import asyncio
import logging

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
)
from langgraph.errors import GraphRecursionError
from langgraph.graph.state import CompiledStateGraph

from app.bootstrap import get_agent
from app.contracts.chat import (
    ChatRequest,
    ChatResponse,
)
from app.service.errors import (
    ExternalResponseError,
    ExternalTimeoutError,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])

AGENT_TIMEOUT_SECONDS = 30.0
AGENT_RECURSION_LIMIT = 100


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    agent: CompiledStateGraph = Depends(get_agent),
) -> ChatResponse:
    logger.info(
        "/chat.request thread_id=%s lat=%s lng=%s message=%r",
        chat_request.thread_id,
        chat_request.location.latitude,
        chat_request.location.longitude,
        chat_request.message,
    )

    try:
        result = await asyncio.wait_for(
            agent.ainvoke(
                {"messages": _turn_messages(chat_request)},
                config={
                    "configurable": {"thread_id": str(chat_request.thread_id)},
                    "recursion_limit": AGENT_RECURSION_LIMIT,
                    "run_name": "chat",
                    "tags": ["chat"],
                    "metadata": {
                        "request_id": getattr(request.state, "request_id", None),
                        "thread_id": str(chat_request.thread_id),
                    },
                },
            ),
            timeout=AGENT_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError as error:
        logger.error("/chat.timeout seconds=%s", AGENT_TIMEOUT_SECONDS)
        raise ExternalTimeoutError(
            code="AGENT_TIMEOUT",
            message="Hit a little traffic. Try sending that again?",
            context={"upstream_status": None},
        ) from error
    except GraphRecursionError as error:
        logger.error("/chat.step_limit limit=%s", AGENT_RECURSION_LIMIT)
        raise ExternalResponseError(
            code="AGENT_STEP_LIMIT",
            message="The assistant could not finish that request. Try rephrasing it.",
            context={"upstream_status": None},
        ) from error

    return ChatResponse(
        reply=_reply_from_result(result),
        thread_id=chat_request.thread_id,
    )


def _turn_messages(chat_request: ChatRequest) -> list[BaseMessage]:
    # Location is request-scoped, so it rides on this turn's HumanMessage.
    # A SystemMessage here would pile up in the checkpointer between turns.
    return [
        HumanMessage(
            content=(
                f"My current location is lat {chat_request.location.latitude}, "
                f"lng {chat_request.location.longitude}.\n"
                f"{chat_request.message}"
            )
        )
    ]


def _reply_from_result(result: dict) -> str:
    messages = result.get("messages") or []
    if not messages:
        raise ExternalResponseError(
            code="AGENT_EMPTY_RESPONSE",
            message="The assistant did not return a reply.",
            context={"upstream_status": None},
        )

    content = messages[-1].content

    return content if isinstance(content, str) else str(content)
