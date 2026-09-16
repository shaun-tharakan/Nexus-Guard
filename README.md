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

---

## 🚀 Setup & Run

> **Follow these steps to run NexusGuard locally.**

### 1. Clone the repository

```bash
git clone <YOUR_REPO_URL>
cd Nexus-Guard
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the Backend

Open **Terminal 1**:

```bash
uvicorn nexus_guard_api:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

### 6. Start the Frontend

Open **Terminal 2**:

```powershell
.\venv\Scripts\Activate.ps1
```

Then:

```bash
streamlit run nexus_guard_frontend.py
```

Open the Streamlit URL shown in the terminal.

---

## How It Works

```text
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
```

The current prototype uses a predefined infrastructure network and rule-based mitigation logic.
