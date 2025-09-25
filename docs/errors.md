# Error Catalogue

The deterministic DSL, LLM parser and clarification engine expose a shared error
model so that clients can react consistently. The table below lists the error
codes that can be emitted at this stage of the project.

| Code  | Component       | Message                                                          | Suggested Action                          |
|-------|-----------------|------------------------------------------------------------------|-------------------------------------------|
| E100  | Rule parser     | No canonical rule matched the sentence.                         | Fall back to the LLM parser or rephrase. |
| E101  | Rule parser     | Coordinate must be in the form `(x,y)` with numeric values.      | Ask the user to correct the coordinate.  |
| E102  | Rule parser     | Circle radius is required for this utterance.                   | Request the radius explicitly.           |
| E103  | Rule parser     | Rectangle width and height are required.                        | Ask for both width and height.           |
| E200  | LLM parser      | LLM provider is not configured.                                 | Ensure provider name/API key is set.     |
| E201  | LLM parser      | Provider response did not satisfy the command schema.           | Retry with stricter instructions.        |
| E300  | Clarification   | Session memory entry has expired.                               | Re-ask the missing information.          |

Each error object is represented by the :class:`app.dsl.errors.ParseError`
exception which carries `code` and `message` properties.
