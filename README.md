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
  - Visualises overall toolpath or exlusively just the selected tool's toolpath frame by frame.

- **Mesh Animation Render Tool**:
  - Visualises the overall part render as an animation in mesh form.

- **STL Viewer**:
  - Visualises the input STL selected by the user from the config.yaml file
  - Allows the user to add markers to obtain accurate position of the part.
  - User can 'auto-inject' where they wish to use the Screwdriver or the VacuumPnP tool.

## Tools

1. **VacuumSuction Tool**
   - **Description**: Controls a vacuum suction tool during printing.
   - **Features**:
     - Configurable suction state and tool movement parameters.
     - Custom G-code generation for vacuum operations.

2. **Screwdriver Tool**
   - **Description**: Controls a screwdriver tool to inject a part during printing.
   - **Features**:
     - Custom G-code generation for screwdriver actions.
     - Customisable start location with tool movement parameters.

3. **Gripper Tool**
   - **Description**: Controls a gripper tool for handling objects during printing.
   - **Features**:
     - Vibration method for part removal.
     - Adjustable parameters for gripper actions for gripper position/angle.
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

3. **Run the Install Script**:
    ```bash
    resources/install.bat
    ```

4. **Run the program**:
- You can run this program as either the python script or as the built exe file that you may have just made.
- If you want to run this as a python script, make sure you're in the parent directory to the main.py file and run:
    ```bash
    python main.py
    ```
- If you want to run this as an application, you can do this through running the exe or pressing the shortcut .lnk file.
    ```bash
    main.exe
    SupremeSlicer.lnk
    ```

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
Released by Pralish Satyal, 27/09/2024.
