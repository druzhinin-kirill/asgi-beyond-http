# ASGI Beyond HTTP - Fleet Management System

A simple fleet management system demonstrating the use of ASGI for handling custom protocols.
This project showcases how to build a server that can process vehicle telemetry data and serve a simple UI interface.


### Running the System

#### 1. Start the Protocol Server

```bash
python -m protocol_server
```

This will start the main server that handles vehicle communications and web requests.

#### 2. Run the Vehicle Emulator

```bash
python tests/emulator/run.py
```

This script simulates vehicle telemetry data.

## Project Structure

- `protocol_server/` - Protocol server implementation
- `application/` - Core application logic and data models
- `framework/` - ASGI framework components
- `teltonika/` - Protocol handling for Teltonika used in Protocol server
- `tests/emulator/` - Vehicle simulation tools

## Usage

1. First, start the protocol server to begin accepting connections
2. Run the emulator to simulate vehicle data transmission
3. Monitor the server output to see real-time fleet data processing

This project demonstrates how ASGI can be extended beyond traditional HTTP use cases
to handle custom protocols in IoT and fleet management scenarios.
