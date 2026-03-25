# Project Rules: THE UNSUNG HERO (Python/Pygame)

## Gameplay Logic
- The "Hero" Knight must be AI-controlled with a "Reckless" state machine.
- Priority: Knight moves toward the highest density of enemies regardless of HP.
- Player: Floating sprite, no attack, dashes to collect "Life Orbs" dropped by enemies.
- Pulse Ability: High knockback but costs 5% of the Knight's current health (Risk/Reward).

## Coding Standards (Python)
- Use PEP 8 styling for all generated code.
- Implement a State Pattern for the Knight's behavior (Idle, Charging, Arrogant/Boasting).
- Ensure all functions include comments explaining the AI's logic for my documentation.

## Collaboration Instructions
- When suggesting code, explain *why* this implementation fits a "Reverse Escort" mission.
- If I ask for a bug fix, provide a "Root Cause Analysis" snippet I can use in my `refinements-changes.md` log.