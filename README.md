# Command And Control Unification Software (CACTUS)

CACTUS is a program that centralises data for Command and Control (C2) agencies in military aviation simulations such as Digital Combat Simulator (DCS).

The were several reasons for the development of CACTUS:

- Airspace Battle Managers (ABMs) often use different software, leading to a lack of cohesion in data sharing and text-based communication.
- Some software used by ABMs is reliant on server-side hosting, meaning that ABMs are reliant on the server hosts to run the software.
- Whilst verbal communication can be effective, it can quite often be misheard or missed entirely, especially during high workloads when sharing information can be pivotal.

## Features
- Easy to run server and client software
- WORDS, Chatroom, and Users tabs
- Full data shared with client upon connection

## Future Features
- Clients will be able to save servers and connect to them without needing to re-enter information
- Custom keybindings (e.g.: switching tabs)
- ATO tab for flight plans and management
- Audio and visual alerts for updates
- Server and client executables

## Compatibility
- Currently, only Windows 10 is supported, but may work on other versions of Windows, MacOS, and Linux.
- Executables will be made for Windows 10/11, Linux, and MacOS where possible.

## Installation

This project uses Poetry for dependency management. To install poetry:

```bash
> pip install poetry
```

To install the dependencies with poetry:

```bash
...\CACTUS> poetry install
```


## Usage

Server:
```bash
...\CACTUS> python server.py
```
Client:
```bash
...\CACTUS> python client.py
```


