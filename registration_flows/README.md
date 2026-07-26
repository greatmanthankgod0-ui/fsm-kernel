# Registration Kernel

A finite state machine (FSM) for conversational registration workflows.

## Structure

- actions/
- guards/
- rules/

Each workflow is defined by:

State → Event → Guard → Action → Next State
