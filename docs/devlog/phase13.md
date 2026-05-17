# Phase 13 Devlog: Git Safety and Diff Artifacts

## Implemented

- Added `nightshift/git.py`.
- Implemented clean-worktree enforcement when `require_clean_worktree` is true.
- Captured pre-run and post-run git status artifacts.
- Wrote per-task `diff.patch` artifacts.
- Handled non-git repositories and git failures gracefully when clean worktree is not required.
- Added git tests with temporary repositories.

## Decisions Made

- Clean-worktree enforcement runs before artifact creation so NightShift does not dirty a repo before checking it.
- If clean worktree is required and git status cannot be read, execution fails safely.
- Diff artifacts are written even when git is unavailable, with a readable explanation instead of crashing.

## Notes

- Existing final reports already include modified files when git status is available.
