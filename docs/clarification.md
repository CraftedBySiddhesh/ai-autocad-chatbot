# Clarification Flows

The clarification engine asks for missing geometry information at field-level
granularity and reuses remembered defaults wherever possible. This document
captures the canonical flows exercised in Stage 06.

## Circle Example

1. **User utterance** → `draw circle at (10,10)`.
2. **Initial pass** → missing radius and centre coordinates trigger three follow-up
   questions (radius, centre X, centre Y).
3. **User answers** → supplies numbers or `use previous value` for defaults.
4. **Ready command** → circle emitted with all numeric fields filled and defaults
   persisted for the session/project.

## Rectangle Example

1. **User utterance** → `rectangle center (0,0)`.
2. **Follow-ups** → width, height, centre X/Y requested.
3. **User says** `use previous value` for width/height.
4. **Engine** pulls widths/heights from session defaults saved by earlier commands.

## Memory Behaviour

- `SessionMemory.set(key, value, persist=True)` stores transient answers and
  updates the project-level default store.
- Repeating commands can reply with "use previous value" to reuse remembered
  dimensions.
- Expired transient values raise error `E300` so the caller can re-ask the user.

These flows are covered by [`tests/test_clarify.py`](../tests/test_clarify.py).
