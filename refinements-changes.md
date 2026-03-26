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






## AI Interaction Log (FIRST EDITION)

- **Entry 1:** Used Cursor to generate a Python script for the Knight's movement. 
- **Observation:** The AI initially made the Knight too smart; I had to re-prompt it to make his pathfinding prioritize the "highest enemy density" to reflect his reckless nature.
- **Entry 2:** Generated the first iteration of the `RecklessKnight` class using Cursor. Implemented a `find_densest_enemy_cluster` function instead of standard pathfinding to ensure the  Knight actively seeks out the most dangerous areas.
- **Entry 3:** Used AI to build the SupportPlayer class. Implemented a vector-based knockback system for the Pulse ability. Directed the AI to enforce the design constraint where using Pulse deducts 5% of the Knight's current HP, creating a functional risk/reward loop.
- **Entry 4:** Used Cursor to implement the combat and healing loop. Added a LifeOrb class. Instructed the AI to ensure the Knight takes minor damage upon enemy collision, reinforcing his recklessness, and built the collection logic for the SupportPlayer to restore his HP.
- **Entry 5:** Playtested the V3 core loop and noticed the Knight was too easily distracted, abandoning fights to chase new swarms. Prompted Cursor to implement a combat_focus_radius (130) and a find_closest_enemy check to create a "local combat lock." Also increased contact_damage from 2.0 to 3.0 to raise the stakes. This iteration successfully forces the Knight to commit to fights, increasing the mechanical pressure on the player to heal him.
- **Entry 6:** Implemented an escalating endless-runner style difficulty system. Directed Cursor to create TankEnemy and RangedEnemy subclasses with distinct behaviors (Tanks are slow but hit hard; Ranged enemies fire tracking projectiles). Updated the spawner to increase frequency and enemy variety based on seconds_survived. Also updated the Player's Pulse ability to clear enemy projectiles, adding a defensive skill ceiling.
- **Entry 7:** Directed Cursor to implement a Boss encounter at the 150-second mark to act as the final survival hurdle. To escalate the mid-game difficulty, I prompted the AI to add a 12-second decay timer to Life Orbs, but specifically tied its activation to the start of the Tank phase (45 seconds). This interconnected system drastically increases the mechanical pressure on the support player. Also used AI to patch a minor stability issue with projectile array iteration.
- **Entry 8:** Prompted Cursor to build a UI overlay to communicate the new difficulty phases. Implemented timed on-screen text warnings for the Tank and Boss phases using Pygame's font module, along with a dedicated UI health bar for the Boss. Instructed the AI to optimize font rendering to maintain the 60 FPS target.
- **Entry 9:** Merged my updated, optimized UI logic (blinking phase warnings and Boss health bar) with the Leonardo AI image loader framework generated by the AI. This required refactoring the draw() methods across all classes to dynamically fall back to colored shapes if the transparent .png files weren't loaded, ensuring stability during testing.
- **Entry 10:** Prompted Cursor to finalize the core gameplay loop by introducing a Game Over state with a 'Press R to Restart' function, a high-score tracker, and an escalating enemy speed multiplier. To increase replayability, I directed the AI to implement an in-run reward system ('Rage Mode' for the Knight at score milestones) and asked the AI to pitch and implement one additional combat polish feature to maximize game feel.
- **Entry 11:** Playtested the core loop and felt the combat lacked impact. Prompted Cursor to add "Game Juice" in the form of brief white-hot (Knight) and gold (Enemy) hit flashes upon contact damage, as well as a camera screen-shake effect when enemies are destroyed. This significantly elevated the game feel and provided crucial visual feedback to the player without altering the underlying collision math.
- **Entry 12:** Integrated the Pygame Mixer module to handle audio. Wrote a safe loading function (play_music) to handle the MusicGPT .mp3 files without crashing. Built a dynamic audio trigger that automatically swaps from the "Triumphant" main theme to the "Frantic" combat theme when tank_phase_active triggers at 45 seconds, perfectly juxtaposing the escalation in gameplay stress. Also added an audio dimming effect upon triggering the Game Over state.
- **Entry 13:** Generated a custom battlefield background using Leonardo AI to finalize the game's dark fantasy aesthetic. I engineered the prompt to strictly enforce the same "top-down overhead perspective" as the character sprites to ensure visual consistency and prevent perspective clashing. To ensure this new, highly-detailed background didn't ruin gameplay readability or obscure the glowing combat auras, I implemented a semi-transparent black overlay surface (bg_dimmer) in Pygame to dynamically dim the map behind the active entities.
- **Entry 14:** Conducted a comprehensive balance pass and UI overhaul. Directed Cursor to implement a full Game State Machine (Main Menu, Rules, Pause, Game Over) and moved the vital Knight HUD to the bottom left for better player readability. Redesigned the "Rage" mechanic from a passive milestone to an active player pickup, and introduced a "Stun Pickup" for the Boss phase to add strategic depth. Balanced the difficulty by increasing Tank durability/damage, speeding up the Knight mid-game, and halving health orb drop rates during the final Boss encounter. Finally, mapped out a complete dynamic audio dictionary for music and SFX.
- **Entry 15:** Conducted focused playtesting and identified a severe difficulty spike during the Tank phase resulting in premature Game Overs, alongside audio clipping issues due to Pygame's default max volume. Prompted Cursor to implement a global audio mix (reducing music to 25% and SFX to 30%). Rebalanced the Tank phase by nerfing Tank contact damage, changing the Tank aura to Dark Orange for better visual hierarchy, and buffering Life Orb drops by 10%. To counter the enemy density, I designed and directed the AI to implement a temporary "Splash Damage" pickup that allows the Knight's strikes to deal AoE damage to clustered enemies.
- **Entry 16:** Conducted final QA testing and identified a state-machine bug preventing the Game Over audio from playing, alongside missing audio feedback for core loops (healing and taking damage). Prompted Cursor to fix the audio trigger logic by tying it strictly to the state transition rather than the frame update. Also directed the AI to implement orb.wav and hit.wav with a cooldown buffer to prevent audio clipping during sustained enemy contact. Finally, overhauled the Rules screen UI to ensure all mechanics (Pulse costs, Rage, Stun) were clearly communicated to the player.
