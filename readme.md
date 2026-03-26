THE UNSUNG HERO
Module: Game Design 3A (GADS7331) | Emeris

Developer: Latita Mvunelo | ST10093388

Platform: PC (Windows Standalone .exe / Python)

Genre: Action / Reverse Escort Survival

📜 Project Overview
"The Unsung Hero" is a frantic, action-based "reverse escort" mission. Instead of playing as the glorious warrior, the player takes on the role of a floating, ethereal support sprite. Your singular objective is to keep a reckless, AI-controlled Hero Knight alive as he charges head-first into an endlessly escalating swarm of dark fantasy enemies. It is a game about the stress, chaos, and lack of appreciation that comes with playing the support class.

🎮 Core Mechanics & Controls
Controls:

W, A, S, D / Arrow Keys: Move the Support Sprite.

SPACEBAR: Cast 'Pulse'.

ESC: Pause Game.

R: Restart (from Game Over screen) / View Rules (from Main Menu).

The Gameplay Loop:

Heal the Hero: Dash across the battlefield to collect glowing Golden Orbs dropped by defeated enemies. Touching an orb instantly heals the Knight.

Manage the Chaos (Pulse): Pressing SPACE casts a massive shockwave that knocks enemies back and destroys incoming projectiles. Warning: Casting Pulse costs 5% of the Knight's current HP. Use it strategically.

Deploy Buffs: Collect spawned power-ups to tip the scales:

Red Diamonds (Rage): Drops after 20 kills in the Tank Phase. Grants the Knight 5 seconds of 150% speed and 50% damage reduction.

Orange Diamonds (Splash): Grants the Knight Area-of-Effect (AoE) melee damage for 8 seconds.

Blue Diamonds (Stun): Spawns during the Boss Phase. Instantly freezes the Warlord for 4 seconds, ending in a massive knockback.

⚔️ The Escalation (Enemy Phases)
The game utilizes a dynamic difficulty state machine that scales over time:

The Swarm (0s - 45s): Basic enemies pursue the Knight. The player establishes the healing loop.

The Tank Phase (45s - 150s): Hulking, high-damage Tanks and Ranged projectile mages enter the fray. Healing Orbs now decay after 12 seconds. The Knight's base speed increases to match the tension, and the audio dynamically shifts from "Triumphant" to "Frantic."

The Warlord Boss (150s+): A massive Boss spawns. Life Orb drop rates are halved (50% chance on kill), forcing the player to rely heavily on Stun pickups and precise Pulse timing.

🤖 AI Integration & Tools Workflow
This prototype was developed during a structured game jam, utilizing Generative AI as a primary creative and technical collaborator to achieve a "Mastered" level of rapid prototyping.

Programming & Logic (Cursor / Claude 3.5 Sonnet & Gemini 3): Used for architectural coding, including the Knight's targeting state machine, the Pygame rendering loop, the dynamic audio mixer, and debugging collision math.

Visual Assets (Leonardo AI): All 2D sprites and the battlefield background were generated using highly engineered prompts to ensure a strict "top-down overhead perspective" and a cohesive, high-contrast dark fantasy 3D-render aesthetic.

Audio (MusicGPT & FreeSound): Dynamic backing tracks were generated to juxtapose the game's phases (a heroic menu theme vs. a frantic combat theme).

Context Management: Custom AI interaction logs (plan.md) were maintained to direct the AI's output, ensuring the human developer remained the "Game Director" at all times. A combination of Gemini and Cursor were used to maintain the AI interaction logs.

⚖️ AI Ethics & Integrity Statement
This project complies strictly with The Independent Institute of Education (IIE) intellectual integrity and fair use policies regarding Generative AI.

Originality & Creative Control: The core "Reverse Escort" concept, the mechanical balancing parameters, and the gameplay loops are original designs by the developer. AI tools were directed via human-in-the-loop prompt engineering to execute specific technical and visual goals.

Transparency: All AI-generated code snippets, visual assets, and audio tracks are explicitly credited within this documentation and the project's development logs.

Responsibility: AI was utilized to enhance workflow efficiency and overcome technical bottlenecks during the jam timeline. All critical design decisions, QA testing, and final implementations remained under the explicit control and review of the human developer.

🚀 Installation & Run Instructions
Option 1: Play the Standalone Executable (Recommended)
No installation required.

Extract the .zip folder.

Double-click TheUnsungHero.exe (or main.exe) to play.

Option 2: Run via Python
Ensure you have Python 3.x installed.

Open your terminal/command prompt in the game directory.

Install the required library: pip install pygame

Run the game: python main.py