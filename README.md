# LISU Framework UI

A modern, user-friendly interface for the LISU (Layered Interaction System for User-Modes) framework, designed to manage multiple degrees-of-freedom input devices for VR applications.

## Features

- Modern, responsive UI with dark/light theme support
- Easy device selection and connection
- Visual control panel for device manipulation
- Real-time status updates
- Automatic configuration management

## Installation

### Prerequisites

- Python 3.7 or higher
- Windows (for `pywinusb`; adaptable to other OS with minor changes)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/MSandovalPhD/MDOF-VR-IndustrialVis-UI.git
   cd MDOF-VR-IndustrialVis-UI
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Select your input device from the dropdown menu
3. Click "Connect Device" to establish connection
4. Use the control panel buttons to manipulate the device

## Configuration

The application automatically creates a default configuration file at `data/visualisation_config.json`. You can modify this file to:

- Add new devices
- Configure UDP settings
- Customize command templates

Example configuration:
```json
{
    "input_devices": {
        "Bluetooth_mouse": {
            "vid": "046d",
            "pid": "b03a",
            "type": "mouse"
        }
    },
    "actuation": {
        "commands": {
            "mouse": "addrotation %.3f 0.0 0.0 %s"
        }
    },
    "visualisation": {
        "render_options": {
            "visualisations": {
                "Drishti-v2.6.4": {
                    "udp_ip": "127.0.0.1",
                    "udp_port": 7755
                }
            }
        }
    }
}
```

## Development

The project structure is organized as follows:

```
MDOF-VR-IndustrialVis-UI/
├── main.py              # Application entry point
├── requirements.txt     # Project dependencies
├── ui/                  # UI components
│   └── main_window.py  # Main window implementation
├── lisu/               # LISU framework integration
│   └── lisu_handler.py # LISU manager implementation
└── data/               # Configuration files
    └── visualisation_config.json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Contributions are welcome! Please fork the repository, make changes, and submit pull requests. For major changes, please open an issue first to discuss.

## Contact

Mario Sandoval - mariosandovalac@gmail.com

All related research papers can be found on [Mario Sandoval Olivé's Academia.edu page](https://manchester.academia.edu/MarioSandovalOliv%C3%A9).

