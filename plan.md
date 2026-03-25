# Development Plan: THE UNSUNG HERO

## Milestones
- [ ] Day 1: Project setup, Git repo, and Basic Movement/Knight AI logic.
- [ ] Day 2: Enemy spawning, Life Orb mechanics, and Pulse ability integration.
- [ ] Day 3: Boss encounter, sound integration (MusicGPT), and final polish.

## AI Tools & Task List
- **Coding (Cursor/Gemini):** Generating the Knight's "Reckless" State Machine and player movement.
- **Art (Leonardo AI):** Generating medieval environment textures and character sprites.
- **Sound (MusicGPT):** Creating the "Triumphant" vs. "Frantic" audio tracks.
- **Documentation (Gemini):** Assisting in refining the AI Ethics Statement.

## AI Interaction Log
*(Note: Use this section to record how the AI helped or where it failed to score high on "Technical Execution".)*
- **Entry 1:** Used Cursor to generate a Python script for the Knight's movement. 
- **Observation:** The AI initially made the Knight too smart; I had to re-prompt it to make his pathfinding prioritize the "highest enemy density" to reflect his reckless nature.
- **Entry 2:** Generated the first iteration of the `RecklessKnight` class using Cursor. Implemented a `find_densest_enemy_cluster` function instead of standard pathfinding to ensure the  Knight actively seeks out the most dangerous areas.
-**Entry 3:** Used AI to build the SupportPlayer class. Implemented a vector-based knockback system for the Pulse ability. Directed the AI to enforce the design constraint where using Pulse deducts 5% of the Knight's current HP, creating a functional risk/reward loop.
-**Entry 4:** Used Cursor to implement the combat and healing loop. Added a LifeOrb class. Instructed the AI to ensure the Knight takes minor damage upon enemy collision, reinforcing his recklessness, and built the collection logic for the SupportPlayer to restore his HP.

## Reflection Notes
*(Keep notes here for your final 200-word reflections at the end of the jam.)*