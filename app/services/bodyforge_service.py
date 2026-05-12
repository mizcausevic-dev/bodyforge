from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, round(value)))


@dataclass(slots=True)
class BodyForgeService:
    source_path: Path

    def load(self) -> dict[str, Any]:
        return json.loads(self.source_path.read_text(encoding="utf-8"))

    def robots(self) -> list[dict[str, Any]]:
        data = self.load()
        events_by_robot: dict[str, list[dict[str, Any]]] = {}
        for event in data["events"]:
            events_by_robot.setdefault(event["robot_id"], []).append(event)

        enriched: list[dict[str, Any]] = []
        for robot in data["fleet"]:
            history = events_by_robot.get(robot["robot_id"], [])
            near_collision_count = sum(1 for event in history if event["event_type"] == "near-collision")
            critical_events = sum(1 for event in history if event["severity"] == "critical")
            risk_score = _clamp(
                robot["speed_mps"] * 18
                + max(0, 3.5 - robot["human_proximity_m"]) * 16
                + (12 if not robot["override_ready"] else 0)
                + critical_events * 18
                + near_collision_count * 11
                + max(0, 55 - robot["battery_pct"]) * 0.45
                + min(robot["last_override_minutes"], 60) * 0.3
            )
            status = "contain" if risk_score >= 76 else "watch" if risk_score >= 48 else "clear"
            next_action = (
                "Freeze task progression, trigger human override, and replay the last movement segment for provenance review."
                if status == "contain"
                else "Reduce speed and hold the robot in the current zone until the supervisor clears the task."
                if status == "watch"
                else "Continue task execution with policy telemetry attached to the run log."
            )
            enriched.append(
                {
                    "robotId": robot["robot_id"],
                    "name": robot["name"],
                    "type": robot["type"],
                    "zone": robot["zone"],
                    "task": robot["task"],
                    "batteryPct": robot["battery_pct"],
                    "humanProximityM": robot["human_proximity_m"],
                    "overrideReady": robot["override_ready"],
                    "safetyPolicy": robot["safety_policy"],
                    "riskScore": risk_score,
                    "status": status,
                    "criticalEvents": critical_events,
                    "nearCollisionCount": near_collision_count,
                    "nextAction": next_action,
                }
            )
        return sorted(enriched, key=lambda item: (-item["riskScore"], item["name"]))

    def events(self) -> list[dict[str, Any]]:
        data = self.load()
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        enriched: list[dict[str, Any]] = []
        robots = {robot["robotId"]: robot for robot in self.robots()}
        for event in data["events"]:
            provenance_score = _clamp(
                (28 if event["override_applied"] else 12)
                + len(event["handoff_chain"]) * 12
                + (18 if event["resolution_state"] in {"contained", "halted"} else 8)
                + (22 if event["severity"] == "critical" else 12 if event["severity"] == "high" else 6)
            )
            enriched.append(
                {
                    "eventId": event["event_id"],
                    "timestamp": event["timestamp"],
                    "robotId": event["robot_id"],
                    "robotName": robots.get(event["robot_id"], {}).get("name", event["robot_id"]),
                    "zone": event["zone"],
                    "severity": event["severity"],
                    "eventType": event["event_type"],
                    "humanPresent": event["human_present"],
                    "policyTriggered": event["policy_triggered"],
                    "handoffChain": event["handoff_chain"],
                    "overrideApplied": event["override_applied"],
                    "resolutionState": event["resolution_state"],
                    "distanceM": event["distance_m"],
                    "provenanceScore": provenance_score,
                }
            )
        return sorted(enriched, key=lambda item: (severity_order[item["severity"]], item["timestamp"]), reverse=False)

    def summary(self) -> dict[str, Any]:
        data = self.load()
        robots = self.robots()
        events = self.events()
        contain = [robot for robot in robots if robot["status"] == "contain"]
        high_events = [event for event in events if event["severity"] in {"critical", "high"}]
        avg_risk = mean(robot["riskScore"] for robot in robots)
        avg_provenance = mean(event["provenanceScore"] for event in events)
        return {
            "facility": data["facility"],
            "site": data["site"],
            "robotCount": len(robots),
            "containCount": len(contain),
            "highSeverityEventCount": len(high_events),
            "averageRiskScore": round(avg_risk, 1),
            "averageProvenanceScore": round(avg_provenance, 1),
            "leadRecommendation": (
                "Keep the high-bay picker and cross-aisle runner inside tighter policy envelopes, then preserve every override and handoff segment so safety investigations can replay the chain without ambiguity."
            ),
        }

    def robot(self, robot_id: str) -> dict[str, Any] | None:
        for robot in self.robots():
            if robot["robotId"] == robot_id:
                return robot
        return None

    def event(self, event_id: str) -> dict[str, Any] | None:
        for event in self.events():
            if event["eventId"] == event_id:
                return event
        return None

    def sample_payload(self) -> dict[str, Any]:
        robots = self.robots()
        events = self.events()
        return {
            "dashboard": self.summary(),
            "fleet": [
                {
                    "robotId": robot["robotId"],
                    "name": robot["name"],
                    "riskScore": robot["riskScore"],
                    "status": robot["status"],
                    "nextAction": robot["nextAction"],
                }
                for robot in robots[:3]
            ],
            "events": [
                {
                    "eventId": event["eventId"],
                    "severity": event["severity"],
                    "eventType": event["eventType"],
                    "resolutionState": event["resolutionState"],
                    "provenanceScore": event["provenanceScore"],
                }
                for event in events[:3]
            ],
        }


def build_service(root: Path | None = None) -> BodyForgeService:
    base = root or Path(__file__).resolve().parents[2]
    return BodyForgeService(base / "app" / "data" / "sample_fleet.json")
