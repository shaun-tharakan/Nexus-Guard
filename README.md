# 🏙️ NexusGuard Pro

NexusGuard Pro is an interactive **urban disaster resilience simulator** that models cascading failures across interconnected critical infrastructure.

It simulates disasters, visualizes infrastructure failures on a map and dependency network, and applies automated mitigation strategies.

## Features

- 🌊 Flood, earthquake, and cyber attack scenarios
- 🗺️ Live infrastructure map
- 🕸️ Dependency/cascade visualization
- 📊 Failure, citizen impact, economic loss & stability metrics
- 🛡️ Automated mitigation
- 📡 Live incident feed

## Tech Stack

- Python
- FastAPI
- NetworkX
- Streamlit
- PyDeck
- Plotly
- Pandas

## Setup

```bash
git clone <YOUR_REPO_URL>
cd Nexus-Guard

python -m venv venv
Windows
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Run
Terminal 1 — Backend
uvicorn nexus_guard_api:app --reload
Terminal 2 — Frontend
.\venv\Scripts\Activate.ps1
streamlit run nexus_guard_frontend.py

Open the Streamlit URL shown in the terminal.

How It Works
Disaster
   ↓
Initial Infrastructure Failure
   ↓
Dependency-Based Cascade
   ↓
Impact Calculation
   ↓
Automated Mitigation
   ↓
Final Infrastructure State

The current prototype uses a predefined infrastructure network and rule-based mitigation logic.
