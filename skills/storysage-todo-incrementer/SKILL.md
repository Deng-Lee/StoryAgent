---
name: storysage-todo-incrementer
description: Implement StorySage by executing the repo-root `to_do.md` plan exactly as written, in one-hour acceptance-sized increments. Use when Codex needs to land the next concrete step from `to_do.md`, define acceptance criteria and test method before coding, make a visible filesystem change in every increment, run verification, self-review the result, adjust if needed, and end with a one-sentence summary.
---

# StorySage To-Do Incrementer

## Workflow

Follow this skill when the task is to implement or advance the StorySage repo according to the repo-root `to_do.md`.

### 0. Load the source of truth first

- Read the repo-root `to_do.md` before planning or coding.
- Treat `to_do.md` as the authoritative implementation sequence, scope boundary, and acceptance source.
- If the user names a specific phase or item, work on that target.
- Otherwise, choose the next incomplete item from the current earliest incomplete phase.
- Read only the code and docs needed for that increment; do not bulk-load unrelated files.

If `to_do.md` is missing, contradictory, or lacks enough detail to implement the next increment safely:

- stop before coding
- report the exact gap
- ask for clarification only on the blocking point

### 1. Define a single acceptance-sized increment

- Split work into increments that are roughly one hour of implementation effort.
- Each increment must be independently verifiable.
- Do not batch multiple increments into one turn unless the user explicitly asks for continuous execution.
- Keep the increment behavior-first, not file-first.
- If the increment cannot produce a concrete filesystem diff, it is not a valid increment.

Before coding, write an increment card in this exact shape:

```md
Increment: <one-sentence increment title>

Acceptance Criteria
- <criterion 1>
- <criterion 2>

Test Method
- <command or manual verification step 1>
- <command or manual verification step 2>

Expected Filesystem Change
- <created/edited file or directory>
```

Rules for the increment card:

- `Increment` must be one sentence and scoped to one increment only.
- `Acceptance Criteria` must describe observable outcomes, not implementation intentions.
- `Test Method` must be executable with available repo commands when possible.
- `Expected Filesystem Change` must name at least one file or directory that will visibly change.

### 2. Implement exactly that increment

- Implement only the scoped increment.
- Prefer modifying the existing structure over introducing parallel abstractions unless `to_do.md` explicitly calls for new layers or files.
- Follow the design already written in `to_do.md`; do not silently redesign it.
- If the code reveals a mismatch with `to_do.md`, pause and reconcile it before continuing.

Every completed increment must leave visible filesystem evidence such as:

- new source files
- edited source files
- new tests
- updated docs that track the landed implementation

Pure analysis, planning-only output, or verbal recommendations do not count as a completed increment.

### 3. Verification is mandatory

After implementation, execute the declared `Test Method`.

- Run the narrowest useful checks first.
- Run repo-native tests, lint, or smoke checks when they exist and are relevant.
- If no automated test path exists for the increment, run the narrowest possible manual verification and describe the observed result concretely.
- Do not declare the increment complete if the declared verification was skipped.

Minimum verification contract:

- every acceptance criterion must be checked against the resulting code or behavior
- every declared test method must actually be executed
- any failed test must be fixed inside the same increment or reported as a blocker

### 4. Self-review before closing the increment

After tests pass, review the actual diff and compare it against the increment card.

Check these questions explicitly:

- Did this increment implement the exact `to_do.md` intent?
- Did the filesystem change match the declared increment scope?
- Did the tests prove the acceptance criteria, or only prove part of them?
- Did this change introduce unnecessary abstraction or drift from the document?
- Is any adjustment required before calling the increment complete?

If adjustment is needed:

- make the adjustment in the same increment
- rerun the affected verification
- repeat the self-review once

If no adjustment is needed:

- end with a one-sentence summary of the increment

### 5. Completion format for each increment

When reporting a completed increment, always include:

1. The increment card
2. What changed on disk
3. The verification actually run
4. The self-review result
5. A one-sentence summary

Use this closing structure:

```md
Self-Review
- Result: <meets expectations / adjusted and now meets expectations / blocked>
- Notes: <short justification>

Increment Summary
<one sentence>
```

## Operating Constraints

- Stay inside the repo-root `to_do.md` plan unless the user explicitly redirects scope.
- Do not jump to a later phase just because it looks easier.
- Do not claim a phase item is implemented unless the code and tests support that claim.
- Do not leave an increment without a visible filesystem change.
- Do not skip acceptance criteria, test method, or self-review.
- Do not stop at analysis when the request is to implement.
- Do not silently weaken the design written in `to_do.md`.
- Prefer small green increments over broad partially verified refactors.

## Decision Rules

- If multiple possible increments exist, choose the smallest one that unblocks the current phase.
- If an increment is too large for one hour, split it before coding.
- If a later increment depends on a missing foundation, build the foundation first.
- If a blocker prevents safe implementation, stop with the blocker instead of inventing a workaround that changes the plan.

## Repo-Specific Notes

- Treat the current repository's `to_do.md` as required input, not optional context.
- Use the detailed first-phase implementation notes in `to_do.md` when working on Prompt Skill internalization.
- When adding runtime, loader, template, or test files described in `to_do.md`, mirror the file names and boundaries from the document unless the user explicitly changes the plan.
