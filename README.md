# FSM Kernel

A reusable Finite State Machine (FSM) execution engine for building modular, state-driven applications.

FSM Kernel separates workflow execution from business logic by managing routing, transitions, sessions, and state progression through a lightweight, reusable kernel.

---

## Philosophy

Large applications eventually become difficult to maintain when workflows are implemented using nested `if`, `elif`, and `switch` statements.

FSM Kernel replaces that approach with predictable state transitions.

Instead of asking:

```
What should happen next?
```

The kernel simply asks:

```
What state am I in?
```

The next action is determined by the workflow itself.

---

# Features

- State-driven execution
- Dynamic routing
- Session management
- Transition engine
- Guard validation
- Workflow registry
- Crash logging
- Persistent storage support
- Modular architecture
- Reusable across multiple projects

---

# Repository Structure

```
fsm-kernel/
│
├── bootstrap.py
├── kernel.py
├── router.py
├── registry.py
├── session.py
├── transition.py
├── transitions.py
├── guards.py
├── storage.py
├── location_picker.py
├── crash_log.py
├── text_helpers.py
├── data/
└── README.md
```

---

# Architecture

```
                User Input
                     │
                     ▼
                 Router
                     │
                     ▼
               FSM Kernel
        ┌────────┼────────┐
        │        │        │
        ▼        ▼        ▼
    Guards   Transition  Registry
        │        │
        └────────┼────────┐
                 ▼        │
             Session      │
                 │        │
                 ▼        │
              Storage ◄───┘
```

---

# Core Components

## Kernel

Coordinates workflow execution.

---

## Router

Routes requests to the correct workflow.

---

## Registry

Keeps track of available workflows.

---

## Session

Maintains user state between interactions.

---

## Transition Engine

Determines the next valid state.

---

## Guards

Validate whether transitions are allowed.

---

## Storage

Persists workflow information.

---

# Typical Flow

```
Input
  │
  ▼
Router
  │
  ▼
Kernel
  │
  ▼
Guard Validation
  │
  ▼
Execute State Logic
  │
  ▼
Transition
  │
  ▼
Next State
```

---

# Design Goals

- Simplicity
- Reusability
- Predictable execution
- Separation of concerns
- Extensibility
- Maintainability

---

# Applications

FSM Kernel can be used for:

- Telegram bots
- Registration systems
- Marketplace workflows
- Business automation
- Customer onboarding
- Multi-step forms
- Interactive assistants

---

# Future Work

- Async execution
- Event-driven workflows
- Rust implementation
- Workflow visualisation
- Universal communication layer integration

---

# License

MIT License
