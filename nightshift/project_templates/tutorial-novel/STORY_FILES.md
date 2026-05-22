# Story File Guide

Use plain Markdown with stable headings. The agents will do better if each file is structured and skimmable.

## `story/worldbuilding.md`

Use this for setting facts, not plot events.

```md
# Worldbuilding

## Premise

## Setting Rules

## Locations

### Location Name
- Summary:
- Culture:
- Power structure:
- Visual details:
- Constraints:

## Magic / Technology / Systems

## Factions

### Faction Name
- Goal:
- Methods:
- Public reputation:
- Secrets:

## Terms / Glossary
- Term: definition
```

## `story/characters.md`

Use this for durable character facts.

```md
# Characters

## Character Name
- Role:
- Age:
- Pronouns:
- Current location:
- Public identity:
- Private goal:
- Fear:
- Voice:
- Relationships:
- Secrets:
- Knows:
- Does not know:
- Physical notes:
- Continuity notes:
```

## `story/style-guide.md`

This is the prose contract.

```md
# Style Guide

## POV
- Example: close third, single POV per scene

## Tense
- Example: past tense

## Tone

## Prose Rules
- Avoid exposition dumps.
- Prefer concrete sensory detail.
- Keep dialogue subtextual.

## Dialogue Rules

## Pacing

## Forbidden Patterns
- No author notes.
- No bracket placeholders.
- No modern slang unless intentional.

## Scene Length
- Target:
- Minimum:
- Maximum:
```

## `story/plot-state.md`

This is the current save file for the story. Update it after each scene.

```md
# Plot State

## Current Story Moment

## Current Character State

### Character Name
- Location:
- Goal:
- Emotional state:
- Injuries/resources/items:
- Knows:
- Believes incorrectly:
- Immediate next pressure:

## Current Conflicts

## Active Secrets

## Recently Changed
- SCENE-001:
```

## `story/timeline.md`

Track chronological order.

```md
# Timeline

## Calendar / Time Rules

## Events

### Day 1 / Morning
- Scene:
- Characters present:
- Event:
- Consequences:

### Day 1 / Evening
```

## `story/unresolved-threads.md`

Track promises to the reader.

```md
# Unresolved Threads

## Open Threads

### Thread Name
- Introduced in:
- What reader knows:
- What characters know:
- Expected payoff:
- Urgency:
- Status: open

## Resolved Threads

### Thread Name
- Resolved in:
- Payoff:
```

## `story/continuity-rules.md`

Hard constraints the agents should not violate.

```md
# Continuity Rules

## Hard Rules
- A character cannot know a secret unless listed in `plot-state.md`.
- Travel between X and Y takes three days.
- Magic cannot resurrect the dead.

## Character Constraints

## Location Constraints

## World System Constraints

## Retcons / Canon Overrides
```

## `story/outline.md`

This is the planned story path. Keep it flexible.

```md
# Outline

## High-Level Arc

## Act 1

### Chapter 1
- Purpose:
- Scenes:
  - SCENE-001:
  - SCENE-002:

## Act 2

## Act 3

## Ending Target
```

## Scene Files

Create scene files under `story/chapters/`.

```md
# SCENE-001: Scene Title

POV: Character Name
Time: Day 1 / Morning
Location: Place

<prose starts here>
```

Main rule: do not write everything everywhere. `worldbuilding.md` is canon facts, `plot-state.md` is current state, `timeline.md` is sequence, and `unresolved-threads.md` is promises/payoffs.
