# 🎮 Welcome to the LeagueSLG Universe: A Letter for Geo

Hey Geo! Welcome to the heart of **LeagueSLG**. If you've ever wondered how a chaotic clash between legendary champions becomes a structured, predictable game, you're in the right place. Think of this project not just as code, but as a digital stadium where we're the architects, the referees, and the coaches all at once.

## 🏛️ The Architecture: How the Stadium is Built

Imagine you're building a massive LEGO set. You don't just throw all the bricks in a pile and hope for a castle. You need a blueprint. Our project follows a clear, layered structure:

1.  **The Chest of Wonders (`/data` & `/db`):** This is where everything lives when the game is "asleep." We use **JSON files** like `champions.json` and `buffs.json` as our source of truth. It's like having a deck of cards where every card's stats are written down permanently.
2.  **The Blueprint (`src/models`):** These are the templates. A `Champion` isn't just a name; it's a complex being with health, attack power, and a memory of what buffs they're currently carrying. We use **Object-Oriented Programming (OOP)** here to make sure every champion behaves like a champion.
3.  **The Brain (`src/logic`):** This is where the magic happens. The `battle` logic acts as the referee, deciding who swings first and how much it hurts. The `effects` and `stats` folders are like the physicists of our world, calculating exactly how a "Bloodlust" buff changes a champion's strength.
4.  **The Conductor (`main.py`):** This is the person waving the baton. It brings everything together to start the simulation and keep it running smoothly.

## 🛠️ Tech Stack: Why These Tools?

We chose **Python** for this project. Why? Because Python is like a Swiss Army knife that’s also really easy to read. In a simulation game (SLG), we do a lot of data manipulation and "if-this-then-that" logic. Python allows us to express these complex rules almost like we're writing in English.

## 🧠 Engineering Wisdom: Lessons from the Trenches

Building this wasn't all sunshine and rainbows. We've had our share of "Aha!" moments and "Oh no!" moments.

### 1. The Great Buff Simplification
Initially, we used complex "Enums" (like a secret code) to handle buffs. It felt professional, but it was like trying to speak a different language just to order coffee. We realized it was much smarter to use **String-Based IDs** directly from our JSON files.
*   **Lesson:** Simple is almost always better. If your code feels like it's fighting you, you're probably overcomplicating it.

### 2. The Language of Documentation
We decided to standardize our Korean comments to be concise and consistent (e.g., using "부여" instead of "부여함").
*   **Lesson:** Clean code isn't just about the logic; it's about how easy it is for another human (or future you) to read. Consistency is the secret sauce of maintainable software.

### 3. The Pitfall of State
In a battle simulation, keeping track of "who has what buff for how many turns" is the hardest part. If you forget to decrement a turn counter, a champion might stay invincible forever!
*   **Pitfall:** Always ensure your "clean-up" logic (removing expired buffs) is as robust as your "creation" logic.

## 🚀 How to Think Like a Pro

A good engineer doesn't just write code that works; they write code that **lives**. They think about:
- **Scalability:** "If I add 100 more champions tomorrow, will my code break?"
- **Readability:** "If Geo looks at this in six months, will he understand what I was thinking?"
- **Resilience:** "What happens if a JSON file is missing a value?"

You're not just building a game, Geo. You're building a system. And every bug we fix is just another brick in a much stronger foundation.

Enjoy the simulation! ⚔️
