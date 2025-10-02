# MX Master 4 Hyprland Integration

A Python application that integrates the Logitech MX Master 4 mouse with Hyprland window manager, providing haptic feedback on window focus changes.

## Features

- HID++ protocol communication with Logitech MX Master 4
- Hyprland event monitoring via socket connection
- Haptic feedback on active window changes
- Debug mode for testing different haptic patterns

## Requirements

- Python 3.12+
- Logitech MX Master 4 mouse
- Hyprland window manager
- `hid` Python library

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd master4
```

2. Install dependencies using uv:
```bash
uv sync
```

Or using pip:
```bash
pip install hid
```

## Usage

### Hyprland Integration

Run the watcher to enable haptic feedback on window changes:

```bash
python watch.py
```

The script will:
- Connect to your MX Master 4 mouse
- Monitor Hyprland window events
- Trigger haptic feedback when you switch windows

### Testing Haptic Patterns

Test different haptic feedback patterns:

```bash
python mx_master_4.py
```

This demo cycles through 15 different haptic patterns with 3-second intervals.

## License

MIT