"""Streamlit dashboard for comparing ARQ protocols."""

import pandas as pd
import streamlit as st

from arq_simulator import simulate_protocol

PROTOCOLS = {
    "Stop-and-Wait": "stop_and_wait",
    "Go-Back-N": "go_back_n",
    "Selective Repeat": "selective_repeat",
}

st.set_page_config(page_title="ARQ Protocol Simulator", page_icon="📡", layout="wide")
st.title("ARQ Protocol Simulator")
st.caption("Compare reliable data transfer under packet and acknowledgement loss.")

with st.sidebar:
    st.header("Simulation settings")
    packet_count = st.slider("Packets to send", 1, 50, 12)
    window_size = st.slider("Sliding window size", 1, 10, 4)
    timeout = st.slider("Timeout (time units)", 2, 20, 5)
    packet_loss = st.slider("Packet loss probability", 0.0, 0.8, 0.15, 0.05)
    acknowledgement_loss = st.slider("ACK loss probability", 0.0, 0.8, 0.10, 0.05)
    seed = st.number_input("Random seed", min_value=0, max_value=1_000_000, value=42)
    run = st.button("Run comparison", type="primary", width="stretch")

if run or "simulation_results" not in st.session_state:
    results = [
        simulate_protocol(
            protocol,
            packet_count=packet_count,
            packet_loss=packet_loss,
            acknowledgement_loss=acknowledgement_loss,
            timeout=timeout,
            window_size=window_size,
            seed=int(seed),
        )
        for protocol in PROTOCOLS.values()
    ]
    st.session_state["simulation_results"] = results
    st.session_state["simulation_settings"] = (
        packet_count,
        window_size,
        timeout,
        packet_loss,
        acknowledgement_loss,
        int(seed),
    )

results = st.session_state["simulation_results"]
settings = st.session_state["simulation_settings"]
if (packet_count, window_size, timeout, packet_loss, acknowledgement_loss, int(seed)) != settings:
    st.info("Settings changed. Select **Run comparison** to simulate with the new values.")

summary = pd.DataFrame(
    [
        {
            "Protocol": name,
            "Delivered": result.packets_delivered,
            "Transmissions": result.packets_sent,
            "Retransmissions": result.retransmissions,
            "Packet losses": result.packet_losses,
            "ACKs lost": result.acknowledgements_lost,
            "Duration": result.duration,
            "Throughput (packets/unit)": round(result.throughput, 3),
        }
        for (name, _), result in zip(PROTOCOLS.items(), results)
    ]
)
st.subheader("Results")
st.dataframe(summary, hide_index=True, width="stretch")
st.bar_chart(summary.set_index("Protocol")[["Transmissions", "Retransmissions"]])

with st.expander("Simulation event traces"):
    for (name, _), result in zip(PROTOCOLS.items(), results):
        st.markdown(f"**{name}**")
        st.code("\n".join(result.trace) or "No events recorded.", language="text")
