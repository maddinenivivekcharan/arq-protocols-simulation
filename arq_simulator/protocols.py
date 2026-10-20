"""Discrete-time simulations of common automatic repeat request protocols."""

from __future__ import annotations

import heapq
import random
from dataclasses import dataclass
from typing import Literal

Protocol = Literal["stop_and_wait", "go_back_n", "selective_repeat"]


@dataclass(frozen=True)
class SimulationResult:
    protocol: Protocol
    packets_sent: int
    retransmissions: int
    packets_delivered: int
    acknowledgements_sent: int
    acknowledgements_lost: int
    packet_losses: int
    duration: int
    trace: tuple[str, ...]

    @property
    def throughput(self) -> float:
        return self.packets_delivered / self.duration if self.duration else 0.0


def simulate_protocol(
    protocol: Protocol,
    packet_count: int = 10,
    packet_loss: float = 0.0,
    acknowledgement_loss: float = 0.0,
    timeout: int = 5,
    window_size: int = 4,
    seed: int = 42,
) -> SimulationResult:
    """Run one ARQ transfer using a seeded, discrete-time channel simulation.

    A data frame and its ACK each take one simulated time unit to travel.
    ``timeout`` must therefore be at least two time units. Packet and ACK
    losses are independently sampled for every transmission attempt.
    """
    if protocol not in ("stop_and_wait", "go_back_n", "selective_repeat"):
        raise ValueError(f"Unsupported protocol: {protocol}")
    if packet_count < 1:
        raise ValueError("packet_count must be at least 1")
    if not 0 <= packet_loss < 1 or not 0 <= acknowledgement_loss < 1:
        raise ValueError("Loss probabilities must be in the range [0, 1)")
    if timeout < 2:
        raise ValueError("timeout must be at least 2 time units")
    if window_size < 1:
        raise ValueError("window_size must be at least 1")

    window = 1 if protocol == "stop_and_wait" else window_size
    rng = random.Random(seed)
    events: list[tuple[int, int, str, int]] = []
    event_order = 0
    outstanding: dict[int, int] = {}
    next_packet = 0
    receiver_expected = 0
    receiver_buffer: set[int] = set()
    delivered: set[int] = set()
    packets_sent = retransmissions = packet_losses = 0
    acknowledgements_sent = acknowledgements_lost = 0
    trace: list[str] = []
    now = 0
    max_time = max(10_000, packet_count * timeout * 100)

    def record(message: str) -> None:
        if len(trace) < 500:
            trace.append(f"t={now}: {message}")

    def schedule(at: int, kind: str, sequence: int) -> None:
        nonlocal event_order
        heapq.heappush(events, (at, event_order, kind, sequence))
        event_order += 1

    def transmit(sequence: int, retransmission: bool) -> None:
        nonlocal packets_sent, retransmissions, packet_losses
        packets_sent += 1
        outstanding[sequence] = now
        if retransmission:
            retransmissions += 1
            record(f"timeout: retransmit packet {sequence}")
        else:
            record(f"send packet {sequence}")
        if rng.random() < packet_loss:
            packet_losses += 1
            record(f"packet {sequence} lost")
        else:
            schedule(now + 1, "frame", sequence)

    while len(delivered) < packet_count or outstanding:
        if now > max_time:
            raise RuntimeError("Simulation exceeded its time limit; check loss and timeout settings")

        while events and events[0][0] <= now:
            _, _, kind, sequence = heapq.heappop(events)
            if kind == "frame":
                if protocol == "selective_repeat":
                    if sequence not in receiver_buffer:
                        receiver_buffer.add(sequence)
                        record(f"receiver buffers packet {sequence}")
                        while receiver_expected in receiver_buffer:
                            delivered.add(receiver_expected)
                            receiver_expected += 1
                    acknowledgements_sent += 1
                    if rng.random() < acknowledgement_loss:
                        acknowledgements_lost += 1
                        record(f"ACK {sequence} lost")
                    else:
                        schedule(now + 1, "ack", sequence)
                else:
                    if sequence == receiver_expected:
                        delivered.add(sequence)
                        receiver_expected += 1
                        record(f"receiver accepts packet {sequence}")
                    else:
                        record(f"receiver discards out-of-order packet {sequence}")
                    ack_sequence = receiver_expected - 1
                    acknowledgements_sent += 1
                    if rng.random() < acknowledgement_loss:
                        acknowledgements_lost += 1
                        record(f"ACK {ack_sequence} lost")
                    else:
                        schedule(now + 1, "ack", ack_sequence)
            elif sequence >= 0:
                if protocol == "selective_repeat":
                    if sequence in outstanding:
                        del outstanding[sequence]
                        record(f"ACK {sequence} received")
                else:
                    acknowledged = [seq for seq in outstanding if seq <= sequence]
                    for seq in acknowledged:
                        del outstanding[seq]
                    if acknowledged:
                        record(f"cumulative ACK {sequence} received")
            # ACK -1 means the receiver has not accepted a packet yet.

        if outstanding:
            if protocol == "selective_repeat":
                expired = [
                    sequence for sequence, sent_at in outstanding.items()
                    if now - sent_at >= timeout
                ]
                for sequence in expired:
                    transmit(sequence, retransmission=True)
            else:
                base = min(outstanding)
                if now - outstanding[base] >= timeout:
                    for sequence in sorted(outstanding):
                        transmit(sequence, retransmission=True)

        while next_packet < packet_count and len(outstanding) < window:
            transmit(next_packet, retransmission=False)
            next_packet += 1

        if len(delivered) == packet_count and not outstanding:
            break
        now += 1

    return SimulationResult(
        protocol=protocol,
        packets_sent=packets_sent,
        retransmissions=retransmissions,
        packets_delivered=len(delivered),
        acknowledgements_sent=acknowledgements_sent,
        acknowledgements_lost=acknowledgements_lost,
        packet_losses=packet_losses,
        duration=now,
        trace=tuple(trace),
    )
