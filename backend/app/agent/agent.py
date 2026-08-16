from langchain_core.tools import BaseTool
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from app.agent.prompt import prompt
from app.core.config import settings
from app.integrations.nvidia.llm_client import NVIDIA_MODEL
from app.service.places.service import GooglePlaceService
from app.service.routes.service import GoogleRoutesService
from app.tools.tools import (
    google_place_tools,
    google_routes_tools,
)

def build_llm() -> ChatNVIDIA:
    return ChatNVIDIA(model=NVIDIA_MODEL, api_key=settings.nvidia_llm_key)

def build_checkpointer() -> MemorySaver:
    return MemorySaver()

def build_agent(
    place_service: GooglePlaceService,
    routes_service: GoogleRoutesService,
    checkpointer: BaseCheckpointSaver,
) -> CompiledStateGraph:
    tools: list[BaseTool] = [
        *google_place_tools(place_service),
        *google_routes_tools(routes_service),
    ]

    return create_react_agent(
        model=build_llm(),
        tools=tools,
        prompt=prompt,
        checkpointer=checkpointer,
    )
