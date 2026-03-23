# How It Works: Continuous AI & Q-Learning

Welcome to the Continuous AI Proof-of-Concept! This document explains in excruciating detail how the entire system works, from the CI/CD pipeline down to the mathematical underpinnings of the Artificial Intelligence agent.

---

## 1. The Continuous AI Architecture

Traditional Machine Learning models are trained in isolated environments, exported as static files, and deployed. **Continuous AI** reimagines this process by integrating the training, evaluation, and deployment directly into the Software Development Life Cycle (SDLC) using GitHub Actions.

### The CI/CD Loop

Whenever a developer modifies `GAMERULES.md` (or any code) and pushes to a feature branch, the following automated pipeline executes:

1. **Environment Spin-up:** GitHub Actions provisions an ephemeral Ubuntu runner and starts a **PostgreSQL 15** service container.
2. **State Restoration (The Brain Implant):** The pipeline attempts to download the latest `dump.sql` from the GitHub Actions Cache. This cache contains the AI's "brain" (the Q-table) from the *previous* run.
3. **Database Initialization:** The pipeline runs `scripts/restore_db.sh` to load the previous brain into the live Postgres container. If it's the very first run, it fails gracefully and initializes a completely blank brain using `scripts/init_db.py`.
4. **Phase 1: Training (`train.py`):** The AI plays 500 games of Tic-Tac-Toe against a random opponent. It explores new strategies, updates its Q-values (its understanding of the game), and saves the updated knowledge back to Postgres using SQL `UPSERT` operations.
5. **Phase 2: Simulation (`simulate.py`):** The AI's "exploration" module is disabled (Epsilon = 0.0). It plays 100 evaluation games using *only* its learned knowledge. The win/loss metrics are appended to `docs/simulation_log.md`.
6. **Phase 3: Auto-Documentation (`generate_docs.py`):** A custom script parses the Python Abstract Syntax Trees (AST) of the codebase, extracts docstrings and classes, and generates clean Markdown files in the `docs/` folder.
7. **Phase 4: Model Export (`export_model.py`):** The Postgres Q-table is queried and dumped into a highly optimized JSON file (e.g., `model_v20231027_120000.json`). The `manifest.json` is updated to record this new "brain level".
8. **State Preservation:** The entire Postgres database is dumped to `dump.sql` and saved back into the GitHub Actions Cache, securely persisting the AI's knowledge for the *next* pipeline run.
9. **Deployment:** Finally, the GitHub Action automatically commits the generated JSON models, logs, and markdown docs back to the feature branch. When merged to `main`, GitHub Pages instantly serves the updated playable web application!

---

## 2. The Artificial Intelligence: Q-Learning Explained

The "brain" of our AI is powered by **Q-Learning**, a model-free reinforcement learning algorithm. It is simple, yet incredibly powerful for turn-based games with a finite number of states.

### Core Concepts

* **Environment:** The Tic-Tac-Toe board.
* **Agent:** Our AI (Model A).
* **State ($S$):** The current configuration of the board. We represent this as a 9-character string (e.g., `"XXO O X  "`). There are roughly 5,478 legal states in Tic-Tac-Toe.
* **Action ($A$):** Placing an 'O' in one of the empty squares (indices 0-8).
* **Reward ($R$):** The feedback the agent receives after the game ends. Win = +1, Loss = -1, Tie = +0.5.
* **Q-Value ($Q(S, A)$):** The "Quality" of a specific action taken from a specific state. It represents the *expected future reward*.
    * If $Q("XXO O X  ", 4) = 0.9$, the AI believes placing its piece in the middle square is a highly winning move.
    * If $Q("XXO O X  ", 8) = -0.5$, the AI believes placing its piece in the bottom right will likely result in a loss.

### The Q-Table (The "Brain")

The AI's brain is literally just a massive lookup table stored in our PostgreSQL database (and exported as JSON). It looks like this:

```json
{
  "X  O X   ": {
    "1": 0.1,
    "2": 0.5,
    "8": -0.2
  }
}
```
When it's the AI's turn, it looks at the board (State), checks the Q-table, and picks the Action with the highest Q-Value.

### How it Learns (The Bellman Equation)

Initially, the Q-table is completely empty. The AI has no idea how to play. During the **Training Phase**, it learns by trial and error using the Bellman Equation:

$$ Q^{new}(S, A) = Q(S, A) + \alpha \cdot \left( R + \gamma \cdot \max_a Q(S', a) - Q(S, A) \right) $$

Let's break down this intimidating formula into plain English:

1. **Current Guess:** $Q(S, A)$ is what the AI currently thinks the move is worth.
2. **The Update Rule (Learning Rate $\alpha$):** We don't want the AI to instantly overwrite its knowledge based on one lucky win. $\alpha$ (alpha, set to 0.5) controls how much of the new information overrides the old information.
3. **The Reward ($R$):** Did we win, lose, or tie the game *because* of this move?
4. **Future Potential (Discount Factor $\gamma$):** $\gamma$ (gamma, set to 0.9) determines how much the AI cares about future rewards. $\max_a Q(S', a)$ looks ahead at the *next* state ($S'$) and asks, "What is the best possible move I have from there?"

In our specific implementation (`train.py`), because rewards are only given at the *end* of the game, we record the history of the entire match. When the game ends, we iterate *backwards* through the moves, applying the reward and discounting it ($\gamma$) for earlier moves.
- The final winning move gets a massive +1 boost.
- The move *before* the winning move gets a slightly smaller boost (+0.9).
- The first move of the game gets a tiny boost.
Over hundreds of games, the AI learns to set up winning scenarios from the very first turn!

### Exploration vs. Exploitation ($\epsilon$-Greedy Strategy)

If the AI *always* chose the highest Q-value, it would find one mediocre strategy and stick to it forever (Exploitation). To discover brilliant new strategies, it must occasionally try random, crazy moves (Exploration).

We control this with **$\epsilon$ (Epsilon)**.
* **During Training:** $\epsilon = 0.3$. 30% of the time, the AI ignores its Q-table and picks a totally random move. This guarantees it explores the entire game tree.
* **During Simulation/Web Play:** $\epsilon = 0.0$. The AI is in "Tournament Mode." It trusts its training 100% and will ruthlessly pick the mathematically optimal move every single time.
