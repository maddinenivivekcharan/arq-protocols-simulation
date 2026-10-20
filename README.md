# ARQ Protocol Simulator

A small Python project that simulates and compares Stop-and-Wait, Go-Back-N,
and Selective Repeat automatic repeat request (ARQ) protocols. It models data
and ACK loss, timeouts, retransmissions, receiver behavior, and eventual packet
delivery. The Streamlit dashboard reports measurements produced by each run.

## Features

- Deterministic, seeded simulations for repeatable experiments.
- Independently configurable packet and acknowledgement loss.
- Stop-and-Wait's single-frame window, Go-Back-N cumulative ACKs and
  retransmission of the outstanding window, and Selective Repeat buffering
  with per-frame acknowledgements and timers.
- Comparison table, transmission chart, and event traces.

## Quick start

Python 3.10 or newer is recommended.

```powershell
cd Projects\arq-protocol-simulator
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
streamlit run app.py
```

The dashboard opens in a browser. Adjust the sidebar parameters and select
**Run comparison** to run a new experiment. A fixed random seed makes a run
reproducible.

## Run a simulation from Python

```python
from arq_simulator import simulate_protocol

result = simulate_protocol(
    "go_back_n",
    packet_count=12,
    packet_loss=0.15,
    acknowledgement_loss=0.10,
    timeout=5,
    window_size=4,
    seed=42,
)
print(result)
```

Supported protocol names are `stop_and_wait`, `go_back_n`, and
`selective_repeat`. Each data frame and its acknowledgement take one simulated
time unit; timeout must be at least two units. Loss probabilities are in
`[0, 1)`.

## Project layout

```text
arq-protocol-simulator/
├── app.py
├── arq_simulator/
│   ├── __init__.py
│   └── protocols.py
├── docs/
│   ├── ARCHITECTURE.md
│   └── INTERVIEW_GUIDE.md
├── tests/
│   └── test_protocols.py
├── requirements.txt
└── README.md
```

See [the architecture overview](docs/ARCHITECTURE.md) and
[the interview guide](docs/INTERVIEW_GUIDE.md) for additional detail.

## Publish to GitHub

After reviewing the created files, initialize and publish the project from its
directory (replace the URL with a repository you created):

```powershell
git init
git add .
git commit -m "Build ARQ protocol simulator"
git branch -M main
git remote add origin https://github.com/<your-user>/arq-protocol-simulator.git
git push -u origin main
```

No Git remote is configured or changed by this project setup.
