from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from nexus_guard_backend import SimulationEngine

app = FastAPI(title="NexusGuard API Integration")
engine = SimulationEngine()

class SimRequest(BaseModel):
    disaster_type: str
    intensity: float
    initial_failures: List[str]
    enable_ai: bool

@app.get("/")
def read_root():
    return {"message": "NexusGuard Backend is Active"}

@app.get("/api/nodes")
def get_nodes():
    return [{"id": n, **d} for n, d in engine.graph.nodes(data=True)]

@app.post("/api/simulate")
def trigger_simulation(req: SimRequest):
    result = engine.run_simulation(
        disaster_type=req.disaster_type,
        intensity=req.intensity,
        initial_failures=req.initial_failures,
        enable_ai=req.enable_ai
    )
    return result