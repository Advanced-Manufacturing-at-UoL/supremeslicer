# SupremeSlicer

## Overview

**SupremeSlicer** extends the capabilities of SuperSlicer by integrating advanced features for generating G-code and toolpaths tailored for specialized tools used in the AMPI Machine. The project enhances SuperSlicer’s usability by offering additional functionalities for various tools, enabling more advanced and customized 3D printing operations.

## Features

- **Terminal Client for SuperSlicer (Native Slicer)**:
  - A terminal-based interface for interacting with SuperSlicer, providing advanced control and functionality over the slicing process.

- **G-code Injection per Tool**:
  - **VacuumSuction Tool**: Injects custom G-code to manage vacuum suction operations.
  - **Screwdriver Tool**: Injects custom G-code for screwdriver operations.
  - **Gripper Tool**: Injects custom G-code for gripper operations.

- **G-code Toolpath Viewer Tool**:
  - Visualises overall toolpath or exlusively just the VacuumPnP toolpath frame by frame.

- **Mesh Animation Render Tool**:
  - Visualises the overall part render as an animation in mesh form.

- **STL Viewer**:
  - Visualises the input STL selected by the user from the config.yaml file
  - Allows the user to add markers to obtain accurate position of the part.
  - User can 'auto-inject' where they wish to use the VacuumPnP tool.

## Tools

1. **VacuumSuction Tool**
   - **Description**: Controls a vacuum suction tool during printing.
   - **Features**:
     - Configurable suction state and tool movement parameters.
     - Custom G-code generation for vacuum operations.

2. **Screwdriver Tool**
   - **Description**: Manages operations for a screwdriver tool used with the 3D printer.
   - **Features**:
     - Custom G-code generation for screwdriver actions.
     - Integration with SuperSlicer for precise tool control.

3. **Gripper Tool**
   - **Description**: Controls a gripper tool for handling objects during printing.
   - **Features**:
     - Adjustable parameters for gripper actions.
     - Custom G-code injection for coordinating gripper movements.

## Getting Started

### Prerequisites

- Python 3.x
- SuperSlicer installed and configured
- AMPI Machine with compatible tools

### Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/PralishSatyal/supremeslicer.git
    ```

2. **Navigate to the Project Directory**:
    ```bash
    cd supremeslicer
    ```

3. **Install Required Python Packages**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Copy the contents from below to the main.spec file after running the install command **:
  - Rebuild the exe with the provided spec file through running:
```bash 
pyinstaller --clean main.spec
```
 
 - Move the exe to the project directory:
(Program should be supremeslicer/main.exe)

### Configuration

- Create or update configuration files for each tool:
  - `vacuum_config.yaml`
  - `screwdriver_config.yaml`
  - `gripper_config.yaml`
  
  Specify the parameters for G-code generation in these files.

- Update the paths in the `configs/config.yaml` file to match your setup.


## Contributing

Contributions to **SupremeSlicer** are welcome provided you have forked the repository and submitted a pull request with your changes. Ensure that your contributions are well-documented and tested.

## Contact

For questions or support, reach out to Pralish via either contact detail: 
[P.Satyal@leeds.ac.uk](mailto:P.Satyal@leeds.ac.uk) 
[pralishbusiness@gmail.com](mailto:pralishbusiness@gmail.com) 

Created by Pralish Satyal, 19/07/2024.
Released by Pralish Satyal, 09/09/2024.
