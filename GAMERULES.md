# Tic-Tac-Toe Game Rules

1. **The Grid:** The game is played on a grid that's 3 squares by 3 squares.
2. **Players:** You are X, your friend (or the computer in this case) is O. Players take turns putting their marks in empty squares.
3. **Winning:** The first player to get 3 of their marks in a row (up, down, across, or diagonally) is the winner.
4. **Draw:** When all 9 squares are full, the game is over. If no player has 3 marks in a row, the game ends in a tie.

---

### ⚠️ Continuous AI Proof-of-Concept

This repository leverages a "Continuous AI" pipeline via GitHub Actions.

**How it works:**
Whenever this `GAMERULES.md` file is modified and pushed, a GitHub Action is triggered.
This action spins up a PostgreSQL database, restores the AI's "brain" (Q-table) from the GitHub cache, trains it for 500 more games against a random opponent, runs a simulation to test its win rate, auto-generates code documentation, and finally saves the updated brain back to the cache!

> **Note on Initial Run:** The very first time this workflow runs (like right now!), the database cache does not exist. The Q-Learning agent starts completely "blank" and untrained. After 500 games, it will learn some basic strategies, but it will not be a perfect player immediately. Every subsequent commit to this file will make the agent smarter as it builds upon its past experiences!
