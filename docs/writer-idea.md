# Agentic Novel Writing Workflow Idea

NightShift could plausibly support non-coding workflows, especially long-form fiction, because the core abstraction is not actually "write code." It is:

- read task context
- call one or more agents
- produce artifacts
- validate outputs
- update project state
- move to the next task

That maps surprisingly well to writing a novel.

## Core Realization

A novel workflow should not ask one model to write the whole book, or even necessarily one whole chapter.

The durable project files would act like the source of truth:

- `worldbuilding.md`
- `characters.md`
- `plot-state.md`
- `style-guide.md`
- `outline.md`
- `chapters/chapter-001.md`
- `chapters/chapter-001-scene-001.md`
- `tasks.md`

The task file would drive the work, similar to coding tasks:

```text
- [ ] SCENE-001: Opening scene at the border checkpoint

Description:
Write the opening scene where Mara tries to enter the city under a false work permit.

Acceptance Criteria:
- Introduces Mara's immediate goal
- Shows the checkpoint culture without exposition dump
- Mentions the salt tax conflict indirectly
- Ends with the inspector noticing the forged seal
- 900-1400 words
- Maintains close third-person POV
```

NightShift would run one scene or section at a time.

## What We Already Have

NightShift already has several useful primitives:

- task files for chunking the novel into scenes or chapter sections
- scoped paths so agents only edit allowed writing/project files
- artifact output so drafts, reviews, and notes are preserved
- retry loops for revision
- planner/reviewer/debugger-style roles
- repo context and semantic context retrieval
- command stages that could run deterministic checks
- file-writer stages that can update Markdown files
- `lookup_requests` so agents can ask to read worldbuilding or prior scenes

That means this may not require a totally new engine. It may mostly need a new template and some writing-specific validation/review stages.

## Likely Workflow

One practical pipeline:

```text
plan_scene
gather_context
draft_scene
validate_scene
continuity_review
style_review
update_plot_state
summarize
```

Possible roles:

- Planner: turns the scene task into a beat plan.
- Context agent: pulls relevant worldbuilding, character, and plot-state excerpts.
- Drafting agent: writes the scene.
- Continuity reviewer: checks contradictions against known state.
- Style reviewer: checks POV, tone, pacing, and prose constraints.
- State updater: updates `plot-state.md`, `characters.md`, and maybe `timeline.md`.

## Chunking Strategy

Do not make a task equal to "write chapter 4" unless chapters are short.

Better units:

- scene
- scene fragment
- chapter section
- revision pass for one scene
- continuity update after one scene
- prose polish for one scene

A chapter can be assembled from multiple scene files:

```text
chapters/
  chapter-001/
    scene-001.md
    scene-002.md
    scene-003.md
  chapter-001.md
```

Then a later command or agent stage can compile `chapter-001.md`.

## Durable State Files

The most important design piece is explicit state.

Recommended files:

```text
story/
  worldbuilding.md
  style-guide.md
  characters.md
  timeline.md
  plot-state.md
  unresolved-threads.md
  continuity-rules.md
  outline.md
  chapters/
```

`plot-state.md` should be updated after every completed scene.

It should track:

- current character locations
- known secrets
- promises made to the reader
- unresolved questions
- relationships
- injuries/resources/items
- timeline date/time
- what each POV character currently knows

This is the fiction equivalent of application state.

## Validation Ideas

Some checks can be deterministic:

- word count range
- file exists
- only allowed files changed
- Markdown heading format
- no forbidden placeholders like `TODO`, `[insert]`, or `TBD`
- no accidental author notes in final prose
- required task terms are present
- output compiles into a chapter file

Some checks need model review:

- continuity with worldbuilding
- character voice consistency
- POV discipline
- pacing
- whether the scene satisfies the beat plan
- whether exposition is too direct
- whether the state update accurately reflects the scene

The key is not to overtrust model review. It should produce actionable retry notes, not silently bless everything.

## What Might Be Missing

### 1. Better Non-Code Templates

This likely needs a dedicated template:

```text
tutorial-deaddrop
tutorial-novel
```

or:

```text
writer-novel
```

The template would include:

- starter story files
- writing prompts
- task examples
- validation commands
- allowed paths
- recommended pipeline

### 2. Better Markdown Patch/File Handling

The current file-writer flow can work, but fiction output may be long. It may be safer to require complete file blocks for one scene file at a time.

The workflow should avoid having an agent rewrite the whole novel or whole `plot-state.md` unless necessary.

### 3. Stronger State Update Governance

The risky part is not drafting prose. The risky part is bad state updates.

Example failure:

- the scene says Mara never saw the prince
- the state updater records that Mara recognized the prince
- future scenes build on the wrong state

A state update should probably be reviewed against the actual scene before being applied.

Possible pipeline:

```text
draft_scene -> review_scene -> propose_state_update -> review_state_update -> apply
```

### 4. Context Window Management

Worldbuilding documents can get large.

The agent should not receive the entire story bible every time. It should receive:

- the current task
- relevant worldbuilding excerpts
- relevant character entries
- recent scene summaries
- current plot state
- style guide

Semantic search is probably enough for a first version, but a novel template may want a more explicit index:

```text
world-index.md
character-index.md
location-index.md
```

### 5. Scene Dependency Tracking

Coding tasks already have dependencies. Fiction tasks would need the same:

```text
Dependencies:
- SCENE-001
- SCENE-002
```

This prevents writing a later scene before the required earlier story state exists.

### 6. Revision Workflows

Writing is not only forward generation.

Useful task types:

- draft new scene
- revise scene for pacing
- revise dialogue
- continuity repair
- line edit
- chapter assembly
- chapter-level review
- update outline after discovery writing

NightShift can already represent these as tasks, but the prompts should distinguish them clearly.

### 7. Output Length Controls

Long fiction output needs explicit limits.

Use:

- scene word count bounds
- `num_predict`
- task acceptance criteria
- smaller scene files

Do not ask for "write chapter 12" unless the chapter has already been broken into beats.

## Suggested First Template

Start with a minimal `writer-novel` template.

Files:

```text
nightshift.yaml
.nightshift/tasks.md
.nightshift/agents/planner.md
.nightshift/agents/drafter.md
.nightshift/agents/continuity-reviewer.md
.nightshift/agents/style-reviewer.md
.nightshift/agents/state-updater.md
story/worldbuilding.md
story/characters.md
story/style-guide.md
story/plot-state.md
story/timeline.md
story/unresolved-threads.md
story/chapters/.gitkeep
```

Pipeline:

```text
plan
semantic_context
context
draft
validate_draft
continuity_review
style_review
update_state
validate_state
summarize
```

Allowed paths:

```yaml
scoped_paths:
  - story
  - .nightshift/tasks.md
```

Draft stage allowed paths:

```yaml
allowed_paths:
  - story/chapters
```

State update stage allowed paths:

```yaml
allowed_paths:
  - story/plot-state.md
  - story/characters.md
  - story/timeline.md
  - story/unresolved-threads.md
```

That separation matters. The drafter should not freely rewrite the world bible, and the state updater should not rewrite the scene prose.

## What We Should Not Do First

Do not start with:

- automatic full-plot generation
- full chapter generation
- global rewrites of all prior chapters
- one giant `worldbuilding.md` dumped into every prompt
- trusting the model to maintain continuity without explicit state files

Those are likely to produce impressive-looking but unstable output.

## Practical First Experiment

A good first test:

1. Create a tiny worldbuilding document.
2. Create three characters.
3. Create five scene tasks.
4. Have NightShift draft one scene at a time.
5. After each scene, update `plot-state.md`.
6. Run continuity review against only the scene, state files, and relevant worldbuilding.
7. Inspect artifacts.

Success criteria:

- scenes land in the right files
- word counts stay bounded
- state updates are accurate
- future scenes use prior state correctly
- reviewers catch obvious contradictions

## Bottom Line

Theoretically, NightShift already has many of the needed utilities.

The missing piece is mostly a writing-oriented template with:

- scene-sized tasks
- durable story state files
- strict path separation between prose and state updates
- writing-specific prompts
- lightweight deterministic validators
- continuity/style review stages

This is viable, but it should start as a constrained scene-writing workflow, not an autonomous novel generator.
