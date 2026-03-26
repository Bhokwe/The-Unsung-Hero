# Development & AI Iteration Log
**Project:** The Unsung Hero
**Developer:** Latita

This document tracks the iterative design process, balancing adjustments, and the integration of Generative AI tools (Cursor, Leonardo AI, MusicGPT) throughout the development of the prototype.

## Phase 1: Core Mechanics & Prototype Initialization
* **Iteration 1:** Established the "Reverse Escort" High Concept. Initialized the Pygame environment using Cursor to generate the foundational 2D movement logic for the Support Player (WASD) and the independent targeting logic for the Reckless Knight.
* **Iteration 2:** Implemented the core resource loop. Directed AI to create `LifeOrb` drops from defeated enemies and established the collision logic required for the player to collect them and heal the Knight.
* **Iteration 3:** Designed the Player's primary active ability ("Pulse"). Iterated on the code to ensure the shockwave consumed 5% of the Knight's HP, introducing a risk/reward tactical layer.
* **Iteration 4:** Refined the Knight's targeting AI. Implemented a `find_densest_enemy_cluster` function to ensure his behavior matched the "reckless" narrative pillar.

## Phase 2: Combat Flow & Difficulty Escalation
* **Iteration 5:** Playtesting revealed the Knight abandoned fights too quickly. Prompted Cursor to add a `combat_focus_radius` (130px) to lock him into local combat, and increased contact damage to raise the stakes.
* **Iteration 6:** Implemented an escalating endless-runner spawner. Introduced `TankEnemy` (high HP/Damage, slow) and `RangedEnemy` (fires tracking projectiles) to force dynamic threat prioritization. 
* **Iteration 7:** Designed a cascading difficulty spike. Tied a 12-second decay timer to `LifeOrbs` specifically during the "Tank Phase" (45s), and implemented a Boss encounter at the 150s mark.
* **Iteration 8:** Added critical UI feedback. Used Pygame's font rendering to flash phase warnings ("TANK PHASE", "BOSS INCOMING") and built a dedicated UI health bar for the Warlord Boss.

## Phase 3: Visual & Audio Asset Integration
* **Iteration 9:** Transitioned to Leonardo AI for visual assets. Engineered prompts utilizing "strictly top-down overhead perspective" and "stylized 3D render" to maintain a cohesive dark fantasy aesthetic. Removed backgrounds for Pygame integration.
* **Iteration 10:** Built a robust image loader with fallback logic. Replaced placeholder circles with Leonardo AI `.png` sprites, adding semi-transparent colored auras beneath them to maintain readability in chaotic combat.
* **Iteration 11:** Generated dynamic audio tracks using MusicGPT. Created a "Triumphant" menu/early-game track and a "Frantic" combat track. 
* **Iteration 12:** Implemented a dynamic audio mixer. Wrote logic to smoothly transition from the triumphant track to the frantic track exactly when the Tank Phase triggers, aligning the audio with the mechanical stress.

## Phase 4: Final Polish & Game Feel (Game Juice)
* **Iteration 13:** Finalized the core arcade loop. Added a definitive Game Over state, a High Score tracker, and a seamless "Press R to Restart" function to drastically improve playtesting quality of life.
* **Iteration 14:** Added "Game Juice." Implemented brief white-hot (Knight) and gold/purple (Enemy) hit flashes upon contact damage, and a camera screen-shake effect on enemy kills to make combat feel punchy.
* **Iteration 15:** Conducted a comprehensive UI overhaul. Implemented a full State Machine (Main Menu, Rules, Pause, Game Over) and moved the Knight's health bar to a fixed HUD element in the bottom left.
* **Iteration 16:** Final Balancing Pass. Nerfed Tank contact damage by 20%, buffered orb drops by 10%, and introduced active power-ups (`RagePickup` for AoE damage, `StunPickup` for the Boss) to give the player strategic counters to the escalating swarms.
* **Iteration 17:** Final QA Audio Pass. Fixed state-transition bugs preventing the Game Over crash sound, and implemented `orb.wav` and `hit.wav` with cooldown buffers to prevent audio clipping during sustained combat. Mixed global audio to 25% (Music) and 30% (SFX).
* **Iteration 18:** Final Deployment. Compiled the Python codebase, image assets, and audio files into a standalone Windows executable (`.exe`) using PyInstaller to ensure frictionless evaluation.