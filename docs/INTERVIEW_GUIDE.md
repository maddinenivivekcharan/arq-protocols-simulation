# Interview Guide

## What does ARQ solve?

Automatic repeat request combines error detection with acknowledgements and
timeouts. A sender retries data when delivery cannot be confirmed, providing
reliable transfer over an unreliable channel.

## Protocol comparison

- **Stop-and-Wait** keeps one unacknowledged frame in flight. It is simple but
  uses the link inefficiently when round-trip delay is large.
- **Go-Back-N** pipelines frames and uses cumulative acknowledgements. A loss
  can cause the sender to retransmit later frames that the receiver discarded.
- **Selective Repeat** pipelines frames, buffers out-of-order arrivals, and
  acknowledges individual frames. It can reduce redundant retransmission but
  requires more receiver state and careful sequence-number management.

## How this project models the channel

Each frame and ACK incurs one simulated time unit. A seeded pseudorandom
generator decides whether each transmission is lost. The event loop processes
arrivals, ACKs, and expired timers, then fills the available sender window.
The result counters and trace come directly from that execution.

## Limitations and discussion

- This is a teaching model, not a network emulator: it omits bit corruption,
  variable delay, congestion, and real sockets.
- Sequence numbers are absolute, rather than bounded and wrapping as they are
  in wire protocols.
- Packet and ACK losses are independent Bernoulli trials.
- The model uses discrete time and a fixed two-unit successful frame/ACK
  round-trip, making protocol behavior easy to inspect and reproduce.
- Throughput is delivered packets divided by simulated time units; it is
  comparative, not a physical link rate.
