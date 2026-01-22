# Agent Behavior Rules

## Non-interactive Execution
- All commands MUST be executed in non-interactive mode.
- Use flags like `-y`, `--yes`, `-f`, or pipes to bypass interactive prompts.
- Ensure scripts do not wait for user input.

## Persistence and Timeout Management
- Apply strict and sufficient timeouts for tool executions.
- Use `WaitMsBeforeAsync` and `WaitDurationSeconds` effectively to ensure tasks are completed or monitored until the user explicitly stops them.
- Do not stop or give up on a task prematurely unless a critical, unrecoverable error occurs or the user intervenes.
