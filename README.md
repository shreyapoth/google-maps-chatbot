# Google Maps Chatbot

FastAPI backend and React (Vite) frontend that finds nearby places and driving routes through the
Google Maps Platform.

## Prerequisites

- Python 3.9 or newer (see the LangChain note under [LLM stack](#llm-stack) before choosing 3.9)
- Node 20.19+ or 22.12+ (required by Vite 8)
- A Google Maps Platform API key with **Places API (New)** and **Routes API** enabled
- An NVIDIA API key from [build.nvidia.com](https://build.nvidia.com); the app will not start without one

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # requirements.txt alone for runtime only
cp .env.example .env                  # then fill in the keys
uvicorn app.main:app --reload --port 8000
```

The API is served at `http://localhost:8000`; interactive docs are at `/docs`.

Dependencies live in three files: `requirements.txt` pins runtime packages, `requirements-dev.txt`
adds the test tools, and `pyproject.toml` carries the looser ranges used when installing the backend
as a package. Add new runtime dependencies to both `requirements.txt` and `pyproject.toml`.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:5173` and expects the backend on port 8000.

## Environment variables

Backend values are read from `backend/.env` (see `backend/.env.example`).

| Variable | Required | Default | Notes |
| --- | --- | --- | --- |
| `GOOGLE_MAPS_SERVER_KEY` | yes | — | Server-side key used for Places and Routes calls |
| `NVIDIA_API_KEY` | yes | — | Startup builds an LLM client, but no endpoint uses it yet |
| `CORS_ORIGINS` | no | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list |
| `LANGSMITH_TRACING` | no | `false` | Set `true` to send agent traces to LangSmith |
| `LANGSMITH_API_KEY` | with tracing | — | Required when tracing is on; get one at [smith.langchain.com](https://smith.langchain.com) |
| `LANGSMITH_PROJECT` | no | `google-maps-chatbot` | LangSmith project the traces land in |
| `VITE_API_URL` | no | `http://localhost:8000` | Frontend only; set in the shell or `frontend/.env` |

`NVIDIA_API_KEY` has no runtime effect today, but `Settings` requires it, so the app will not start
without a value.

## LLM stack

The model is Meta's `meta/llama-3.3-70b-instruct`, hosted by NVIDIA and reached through two
interchangeable clients:

| Client | Package | Where |
| --- | --- | --- |
| `AsyncOpenAI` pointed at NVIDIA | `openai` | `bootstrap.py`, `integrations/nvidia/llm_client.py` |
| `ChatNVIDIA` | `langchain-nvidia-ai-endpoints` | `agent/agent.py` |

The `openai` package appears here because NVIDIA's NIM endpoint implements the OpenAI
`/v1/chat/completions` API. Setting `base_url` to `https://integrate.api.nvidia.com/v1` sends every
request to NVIDIA, authenticated with `NVIDIA_API_KEY` — no request reaches OpenAI, and the `model`
string selects from what NVIDIA hosts. The LangChain path uses NVIDIA's own integration instead, so
it needs no `base_url` override.

`agent/agent.py` builds a tool-calling agent with `create_react_agent` from `langgraph.prebuilt`,
handing it the `@tool`-decorated functions in `tools/tools.py`. `POST /chat` invokes that agent.

## LangSmith tracing

LangGraph records every model call and tool call automatically once tracing is on. Set
`LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` in `backend/.env`, then restart uvicorn.
`bootstrap.configure_tracing` copies those Settings values into the process environment LangChain
reads. Each `/chat` run is named `chat` and tagged with the request id, so a 502 in the server log
can be matched to the trace at [smith.langchain.com](https://smith.langchain.com).

```bash
# recent traces for this project
langsmith trace list --project google-maps-chatbot --limit 10 --api-key $LANGSMITH_API_KEY
langsmith trace list --project google-maps-chatbot --error --last-n-minutes 60 --api-key $LANGSMITH_API_KEY
```

**LangChain on Python 3.9:** the newest installable release is the 0.3 line, because LangChain 1.x
requires Python 3.10 or newer. Most current LangChain documentation targets 1.x, where imports and
the agent APIs differ — notably `langchain.agents.create_agent`, which does not exist in 0.3, so the
agent comes from `langgraph.prebuilt` instead. Use Python 3.11+ to follow those docs; that also
removes the need for the `eval-type-backport` shim.

## Tests

```bash
cd backend && source .venv/bin/activate && pytest
cd frontend && npm test -- --run
```

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness check |
| POST | `/places/nearby` | Places within a radius of a point, filtered by type |
| POST | `/places/text-search` | Free-text place search |
| POST | `/routes/directions` | Driving route from a coordinate to an address |

```bash
curl -X POST http://localhost:8000/places/nearby \
  -H 'Content-Type: application/json' \
  -d '{"included_types":["restaurant"],"location":{"latitude":37.33,"longitude":-121.89},"radius":5000,"max_results":5}'
```

## Layout

Requests flow router → service → integration client → Google.

```
backend/app
├── bootstrap.py    Builds every client and service at startup, plus the Depends accessors
├── api/            FastAPI routers
├── contracts/      Request and response models for this API
├── core/           Settings, HTTP transport policy, external URLs
├── integrations/   Google wire models, request builders, clients, mappers
│   └── nvidia/     LLM client and model selection
├── service/        Orchestration and error translation
└── utils/          Unit conversions
```

`bootstrap.py` is the composition root: it owns the lifespan, stores the shared clients and services
on `app.state`, and is the only module that reads those state keys. It sits above `core/` because it
imports from every layer, while `core/` is imported by all of them.

`contracts/` describes shapes this API exposes; `integrations/**/models.py` describes shapes Google
returns. Mappers convert between the two so upstream field names never leak into the public API.
