# BussDCC Framework

**bussdcc-framework** is an opinionated runtime and tooling layer built on top of `bussdcc`.

It provides the components most real systems need:

* runtime orchestration
* event sinks and replay
* JSONL event logging
* a lightweight web interface
* system identity discovery
* deterministic replay of recorded event streams

The framework keeps the **bussdcc kernel small** while providing a practical foundation for building complete systems.

# Architecture

```
Application
    ↓
bussdcc-framework
    ↓
bussdcc
```

### bussdcc (kernel)

The core provides the minimal primitives:

* messages
* events
* processes
* services
* runtime
* state
* clocks
* event buses

### bussdcc-framework

The framework adds system-level capabilities:

* structured event logging
* replay runtime
* web interface
* event sinks
* operational services
* application scaffolding

# Features

## Runtime

Extended runtime with event sinks and framework lifecycle messages.

```python
from bussdcc_framework.runtime import Runtime

runtime = Runtime()
```

Features:

* event sink pipeline
* framework lifecycle messages
* graceful shutdown handling
* replay support

## Event Logging (JSONL)

Built-in JSONL logging for deterministic replay and auditing.

```python
from bussdcc_framework.io.jsonl import JsonlSink

runtime.add_sink(JsonlSink("./events"))
```

Logs are segmented by time:

```
events/
  2026-03-09/
    12-00-00.jsonl
    12-10-00.jsonl
```

Each line contains a structured event:

```json
{
  "time":"2026-03-09T12:00:01Z",
  "message":"system.identity",
  "data":{ ... }
}
```

## Event Replay

Replay previously recorded event streams.

```python
from bussdcc_framework.runtime import ReplayRuntime
from bussdcc_framework.io.jsonl import JsonlSource

runtime = ReplayRuntime(speed=1.0)

runtime.add_source(JsonlSource("./events"))
```

This allows:

* deterministic testing
* system simulation
* historical debugging

## Web Interface

A lightweight Flask + Socket.IO interface for system control and monitoring.

```python
from bussdcc_framework.interface.web import WebInterface

runtime.add_process(
    WebInterface(host="0.0.0.0", port=5000)
)
```

Custom routes can be registered:

```python
class MyWeb(WebInterface):

    def register_routes(self, app, ctx):

        @app.route("/")
        def index():
            return "Hello World"
```

Inside Flask routes you can emit BussDCC messages:

```python
from bussdcc_framework.interface.web import emit

emit(MyMessage())
```

## Console Logging

Simple JSON event output for development.

```python
from bussdcc_framework.io.console import ConsoleSink

runtime.add_sink(ConsoleSink())
```

Example output:

```
{"time":"2026-03-09T12:00:01Z","message":"framework.booted","data":{"version":"0.1.0"}}
```

## System Identity Service

Discovers system metadata at runtime:

* hostname
* hardware model
* CPU serial

```python
from bussdcc_framework.service import SystemIdentityService

runtime.add_service(SystemIdentityService())
```

This emits a `SystemIdentityEvent` and stores it in runtime state.

# Example

Minimal application:

```python
from bussdcc_framework.runtime import Runtime
from bussdcc_framework.io.console import ConsoleSink
from bussdcc_framework.service import SystemIdentityService

runtime = Runtime()

runtime.add_sink(ConsoleSink())
runtime.add_service(SystemIdentityService())

runtime.boot()
runtime.run()
```

# Design Goals

### Deterministic systems

All behavior flows through events that can be logged and replayed.

### Strong typing

All messages are typed dataclasses.

### Operational visibility

Event streams are easily captured and analyzed.

### Replayable execution

Recorded systems can be replayed exactly for debugging and simulation.

### Small core

The `bussdcc` kernel stays minimal while the framework provides practical tooling.

# Installation

```bash
pip install bussdcc-framework
```

# Related Projects

* **bussdcc** – event-driven systems kernel
* **bussdcc-hardware** – hardware device integrations

# License

MIT License
