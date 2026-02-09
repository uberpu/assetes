# ARCANA GRID TACTICS — CORE GAME RULES

This document defines the **authoritative gameplay rules** for Arcana Grid Tactics. It excludes AI behavior, generators, rendering, and implementation notes.

---

## 1. Core Identity

Arcana Grid Tactics is a deterministic strategy game played on a **landscaped square grid**. The grid may be irregular in topology, elevation, and terrain. Maps are constructed to force interaction rather than symmetry.

Tone:

- Playful
- Cruel
- Ascetic

---

## 2. The Magus

Each player controls one or more **Magus** entities.

All Magi:

- exist as units on the board
- can move, fight, cast, absorb, and merge
- are valid win-condition targets

There is no special distinction between original and cloned Magi.

---

## 3. Towers

Towers are the primary organs of control.

Rules:

- A Magus must occupy a tower to perform **work**.
- Work includes casting, summoning, commanding, and activating abilities.
- Outside a tower, a Magus may only move, defend, be attacked, or die.

Non-mage units may not enter a tower unless a Magus is present.

---

## 4. Magus Creation (Cloning)

A player may create additional Magi by:

- occupying an eligible tower (opposite or paired)
- sacrificing a character in that tower

New Magi begin at minimum stats.

---

## 5. Units, Damage, and Absorption

Units may die by damage, hazards, terrain effects, or absorption.

Absorption is the most favorable kill outcome and enables fusion.

---

## 6. Motion, Stance, and Flip Rules

Facing encodes **stance indices**, not cosmetic direction.

### North / South — Support Cycle

1. Heal
2. Shield
3. Special

- North advances: `1 → 2 → 3 → 1`
- South reverses: `3 → 2 → 1 → 3` (cycle)

### East / West — Combat Cycle

A. Strong attack / weak defense
B. Neutral
C. Weak attack / strong defense

- East advances: `A → B → C → A`
- West reverses: `C → B → A → C`

A flip is always movement to an adjacent tile.

### Turtle Move

- Costs AP
- No movement
- Resets both cycles
- Restores shield
- No attack or special

---

## 7. Action Point Economy

- AP is generated per Magus
- Actions resolve immediately when paid
- More Magi = more agency

Action cost tiers: High (move, cast), Medium (summon, assign), Low (prep), Lowest (influence).

---

## 8. Assignment and Autonomous Motion

Magi assign destinations; units travel autonomously.

Influence allows costly direct intervention.

---

## 9. Victory

Victory occurs when:

- all opposing Magi are dead, OR
- square-based victory pressure resolves in a player’s favor.

