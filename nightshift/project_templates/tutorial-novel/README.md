# NightShift Novel Tutorial

This template is a scene-sized fiction writing workflow.

Create it with:

```bash
nightshift init --template tutorial-novel --root my-novel
```

Fill in the private story files under `story/` before running the first scene task. The generated project `.gitignore` ignores those files by default so worldbuilding, outlines, and drafts do not accidentally get committed.

Use [STORY_FILES.md](STORY_FILES.md) for the recommended structure of each story file.

Core files:

```text
story/worldbuilding.md
story/characters.md
story/style-guide.md
story/plot-state.md
story/timeline.md
story/unresolved-threads.md
story/continuity-rules.md
story/outline.md
story/chapters/
```

Run:

```bash
nightshift validate
nightshift run --task SCENE-001
```

Or run it in an isolated integration sandbox from the NightShift repository root:

```bash
python -m nightshift.cli integ-test --template tutorial-novel --task SCENE-001
```

The pipeline drafts one scene file, reviews it for continuity and style, then updates durable state files. Keep tasks scene-sized. Do not ask the model to write the whole novel or a full chapter unless the chapter is short and tightly outlined.
