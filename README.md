# SupremeSlicer

## Overview

**SupremeSlicer** is a project designed to extend the capabilities of SuperSlicer by integrating additional functions for generating G-code and toolpaths for specialized tools used in the AMPI Machine. The project aims to bridge the usability of SuperSlicer with enhanced features that support various tools, enabling more advanced and customized 3D printing operations.

## Features

- **Terminal Client for SuperSlicer (Native Slicer)**:
  - A terminal-based client that allows for interaction with SuperSlicer, providing additional functionality and control over the slicing process.

- **G-code Injection per Tool**:
  - **VacuumSuction Tool**: Injects custom G-code for vacuum suction operations.
  - **Screwdriver Tool**: Injects custom G-code for screwdriver operations.
  - **Gripper Tool**: Injects custom G-code for gripper operations.

- **Overall G-code Simulation Tool**:
  - Simulates the generated G-code to visualize and verify toolpaths before actual printing.

## Tools

1. **VacuumSuction Tool**
   - **Description**: Provides functionality to control a vacuum suction tool during printing.
   - **Features**:
     - Configurable parameters for suction state and tool movement.
     - G-code generation and injection for vacuum operations.

2. **Screwdriver Tool**
   - **Description**: Manages the operations of a screwdriver tool used in conjunction with the 3D printer.
   - **Features**:
     - Custom G-code generation for screwdriver actions.
     - Integration with SuperSlicer for precise tool control.

3. **Gripper Tool**
   - **Description**: Controls a gripper tool for handling objects during the printing process.
   - **Features**:
     - Adjustable parameters for gripper actions.
     - G-code injection to coordinate gripper movements.

## Getting Started

### Prerequisites

- Python 3.x
- SuperSlicer installed and configured
- AMPI Machine with compatible tools

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/PralishSatyal/supremeslicer
    ```

2. Navigate to the project directory:
    ```bash
    cd supremeslicer
    ```

3. Install required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

- Create or update the configuration files for each tool (e.g., `vacuum_config.yaml`, `screwdriver_config.yaml`, `gripper_config.yaml`) to specify the parameters for G-code generation.
- Update the paths in the `main.py` file to match your setup.

### Usage

1. Run the Terminal Client:
    ```bash
    python main.py
    ```

2. Follow the prompts to choose the tool, generate and inject G-code, or simulate the overall G-code.

### Example

To inject G-code for the VacuumSuction Tool:

1. Select the option to generate and inject G-code.
2. Enter the height where the G-code should be injected.
3. Provide the output path where the modified G-code will be saved.

## Contributing

Contributions to **SupremeSlicer** are welcome. Please fork the repository and submit a pull request with your changes. Ensure that your changes are well-documented and tested.

## Contact

For any questions or support, please reach out to [pralishbusiness@gmail.com](mailto:pralishbusiness@gmail.com). Created by Pralish Satyal 22/07/2024. 
