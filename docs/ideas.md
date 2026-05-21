# Ideas TODO

This file tracks open ideas only. Completed items should be removed after they land.

Priority scale:

- P0: do next; directly improves current feedback loop
- P1: important after the current loop is usable
- P2: useful, but only after basics are stable
- P3: defer or maybe reject

## P1: Add Test Governance For Generated Tests

Use this only for generated-test mode. Do not put generated tests back into the default DeadDrop fixed-test pipeline yet.

The previous failures proved test-writing agents will:

- edit app code
- import nonexistent modules
- require undeclared dependencies
- inspect implementation internals
- write tests for future behavior

Governance should be deterministic first, model-reviewed second.

Deterministic checks:

- test-writing stage may only touch `tests/`
- tests compile
- tests import only allowed public interfaces
- tests do not import undeclared dependencies
- tests do not define Flask routes or app implementation
- test names match current task id or current artifact
- no future-task keywords unless accepted by current task acceptance criteria

Then optional model reviewer checks acceptance-criteria alignment.

## P2: Add A Test Analyzer Agent For TDD

Defer until generated tests are stable.

Possible pipeline:

```text
write_tests -> validate_tests -> analyze_tests -> implement
```

Analyzer output should be concrete:

```text
Implementation requirements:
- create_app(database_path) must return a Flask app.
- POST /snippets must return 201 and JSON id.
- GET /snippets/<id> must return persisted fields.

Do not modify:
- tests/test_task001.py
```

This may help smaller models, but it is another model output that can be wrong. Add it only after the fixed-test pipeline works through all DeadDrop tasks.

## P2/P3: Add A Test Planner

Maybe, but defer.

This overlaps with:

- planner
- test analyzer
- test governance

Too many planning-ish stages can make the pipeline bloated and contradictory.

If implemented later, keep it focused:

```text
test_planner -> write_tests -> test_governance -> implement
```

For now, fold this idea into the future test governance/analyzer work.

## P2: Add Run Comparison

Useful once comparing 14B vs 30B:

```powershell
nightshift compare-runs --latest 5
```

Show:

- model
- task
- retries
- failure stage
- final reason
- runtime
- token estimate

This should come after `integ-test` and `integ-report`.

## P2: Add A Separate Multiagent/Fallback DeadDrop Experiment

Keep the default DeadDrop template boring and deterministic:

```text
planner -> semantic_context -> context -> implement -> validate -> test -> review
```

If fallback is useful, put it in a separate experiment template, for example:

```text
tutorial-deaddrop-multiagent
```

or:

```text
examples/templates/multiagent-fallback
```

Reason:

- fallback makes artifacts harder to reason about
- model variability is bad while debugging pipeline behavior
- the default template should remain the reliability harness
