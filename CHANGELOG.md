# Changelog

All notable changes to this project are documented here.

## [1.0.0] - 2026-05-12

### Released
- Published **bodyforge** as the flagship embodied-AI governance repo in the portfolio.
- Packaged zone policy, collision provenance, override logic, event replay, and operator-facing incident review into one coherent public system.
- Shifted the repo from "future robotics concept" to "credible control-plane software for mixed human and robot environments."

### Why this mattered
- Robotics demos often emphasize motion and autonomy while under-explaining the governance layer operators actually need.
- Safety review, override chains, and incident reconstruction are easier to hand-wave than to productize.
- This release made the repo legible to robotics startups, factory automation teams, and buyers thinking about operational trust.

## [0.1.0] - 2026-02-15

### Shipped
- Locked the first internal model for fleet state, safety incidents, zone rules, and human override events.
- Added the first review surfaces for inspecting why a robot was slowed, rerouted, or escalated.

## [Prototype] - 2025-04-11

### Built
- Built the earliest prototype around collision-risk evaluation, override provenance, and handoff logging.
- Tested whether the repo could support incident reconstruction instead of just live telemetry.

## [Design Phase] - 2023-10-08

### Designed
- Chose a governance and safety framing instead of a generic robotics dashboard.
- Put operator trust, not motion novelty, at the center of the design.
- Kept the outputs aligned with how industrial teams actually review events after something looks wrong.

## [Idea Origin] - 2023-02-08

### Observed
- The idea came from a simple question: what does the software layer look like between autonomous behavior and human accountability?
- The missing artifact was a control surface for embodied AI that treated collision provenance and override logic as first-class concerns.