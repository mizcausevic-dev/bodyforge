from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bodyforge_service import build_service


class BodyForgeServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = build_service(ROOT)

    def test_summary_shape(self) -> None:
        summary = self.service.summary()
        self.assertEqual(summary["facility"], "Northstar Fulfillment Robotics Campus")
        self.assertGreater(summary["robotCount"], 0)

    def test_critical_event_lookup(self) -> None:
        event = self.service.event("evt-9003")
        self.assertIsNotNone(event)
        self.assertEqual(event["severity"], "critical")

    def test_high_bay_picker_is_not_clear(self) -> None:
        robot = self.service.robot("rb-408")
        self.assertIsNotNone(robot)
        self.assertIn(robot["status"], {"watch", "contain"})


if __name__ == "__main__":
    unittest.main()
