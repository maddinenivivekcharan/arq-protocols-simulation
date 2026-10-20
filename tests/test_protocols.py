import unittest

from arq_simulator import simulate_protocol


class ProtocolSimulationTests(unittest.TestCase):
    def test_all_protocols_deliver_every_packet_without_loss(self):
        for protocol in ("stop_and_wait", "go_back_n", "selective_repeat"):
            with self.subTest(protocol=protocol):
                result = simulate_protocol(protocol, packet_count=8, seed=4)
                self.assertEqual(result.packets_delivered, 8)
                self.assertEqual(result.retransmissions, 0)
                self.assertEqual(result.packets_sent, 8)
                self.assertEqual(result.packet_losses, 0)

    def test_lossy_channel_retransmits_and_eventually_delivers(self):
        for protocol in ("stop_and_wait", "go_back_n", "selective_repeat"):
            with self.subTest(protocol=protocol):
                result = simulate_protocol(
                    protocol,
                    packet_count=12,
                    packet_loss=0.25,
                    acknowledgement_loss=0.25,
                    timeout=5,
                    window_size=4,
                    seed=17,
                )
                self.assertEqual(result.packets_delivered, 12)
                self.assertGreater(result.retransmissions, 0)
                self.assertGreater(result.packet_losses + result.acknowledgements_lost, 0)

    def test_stop_and_wait_uses_one_packet_window(self):
        result = simulate_protocol(
            "stop_and_wait", packet_count=5, packet_loss=0.2, seed=9, window_size=4
        )
        self.assertEqual(result.packets_delivered, 5)
        self.assertGreaterEqual(result.duration, 10)

    def test_selective_repeat_avoids_unnecessary_window_retransmissions(self):
        settings = {
            "packet_count": 8,
            "packet_loss": 0.2,
            "timeout": 4,
            "window_size": 4,
            "seed": 2,
        }
        go_back_n = simulate_protocol("go_back_n", **settings)
        selective_repeat = simulate_protocol("selective_repeat", **settings)
        self.assertEqual(go_back_n.packets_delivered, 8)
        self.assertEqual(selective_repeat.packets_delivered, 8)
        self.assertLess(selective_repeat.retransmissions, go_back_n.retransmissions)

    def test_acknowledgement_loss_causes_recovery(self):
        result = simulate_protocol(
            "stop_and_wait",
            packet_count=8,
            acknowledgement_loss=0.3,
            timeout=5,
            seed=17,
        )
        self.assertEqual(result.packets_delivered, 8)
        self.assertGreater(result.acknowledgements_lost, 0)
        self.assertGreater(result.retransmissions, 0)

    def test_invalid_settings_are_rejected(self):
        invalid_cases = (
            {"protocol": "unknown"},
            {"packet_count": 0},
            {"packet_loss": 1},
            {"acknowledgement_loss": -0.1},
            {"timeout": 1},
            {"window_size": 0},
        )
        for settings in invalid_cases:
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                simulate_protocol(**({"protocol": "go_back_n"} | settings))


if __name__ == "__main__":
    unittest.main()
