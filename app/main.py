from __future__ import annotations

import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from app.render import render_api_summary, render_event_replay, render_incident_board, render_overview
from app.services.bodyforge_service import build_service

app = FastAPI(
    title="BodyForge",
    version="0.1.0",
    description=(
        "Real-time governance and safety control plane for embodied AI fleets in warehouses, factories, and mixed human-robot environments."
    ),
)

service = build_service()


@app.get("/", response_class=HTMLResponse)
def overview() -> str:
    return render_overview()


@app.get("/event-replay", response_class=HTMLResponse)
def event_replay() -> str:
    return render_event_replay()


@app.get("/incident-board", response_class=HTMLResponse)
def incident_board() -> str:
    return render_incident_board()


@app.get("/api-summary", response_class=HTMLResponse)
def api_summary_page() -> str:
    return render_api_summary()


@app.get("/api/dashboard/summary")
def dashboard_summary() -> dict:
    return service.summary()


@app.get("/api/robots")
def robots() -> list[dict]:
    return service.robots()


@app.get("/api/events")
def events() -> list[dict]:
    return service.events()


@app.get("/api/robots/{robot_id}")
def robot(robot_id: str) -> dict:
    value = service.robot(robot_id)
    if value is None:
        raise HTTPException(status_code=404, detail="Robot not found")
    return value


@app.get("/api/events/{event_id}")
def event(event_id: str) -> dict:
    value = service.event(event_id)
    if value is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return value


@app.get("/api/sample")
def sample() -> dict:
    return service.sample_payload()


@app.get("/openapi.json")
def openapi_spec() -> JSONResponse:
    return JSONResponse(json.loads(json.dumps(app.openapi())))


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", "4829"))
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=False)
