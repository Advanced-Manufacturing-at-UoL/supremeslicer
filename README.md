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

- **Overall G-code Simulation Tool**:
  - Visualizes and verifies generated G-code to ensure accurate toolpaths before actual printing.

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
  - Compile the file into one exe and generate generic spec file

  ```bash
  pyinstaller --onefile main.py
  ```
 - Copy over the spec file from below to the main.spec file
```bash 
  # -*- mode: python ; coding: utf-8 -*-
  a = Analysis(
      ['main.py'],
      pathex=[],
      binaries=[],
      datas=[
          ('lib', 'lib'),
          ('tools', 'tools'),
          ('configs','configs'),
          ('tools', 'tools'),
          ('input', 'input'),
          ('output', 'output')
      ],
      hiddenimports=[],
      hookspath=[],
      hooksconfig={},
      runtime_hooks=[],
      excludes=[],
      noarchive=False,
  )
  pyz = PYZ(a.pure)

  exe = EXE(
      pyz,
      a.scripts,
      a.binaries,
      a.datas,
      [],
      name='main',
      debug=False,
      bootloader_ignore_signals=False,
      strip=False,
      upx=True,
      upx_exclude=[],
      runtime_tmpdir=None,
      console=True,
      disable_windowed_traceback=False,
      argv_emulation=False,
      target_arch=None,
      codesign_identity=None,
      entitlements_file=None,
  )
```
 
 - Rebuild the exe through running:
```bash 
pyinstaller --clean main.spec
```

### Configuration

- Create or update configuration files for each tool:
  - `vacuum_config.yaml`
  - `screwdriver_config.yaml`
  - `gripper_config.yaml`
  
  Specify the parameters for G-code generation in these files.

- Update the paths in the `main.py` file to match your setup.

### Usage as a Python Script

1. **Run the Terminal Client**:
    ```bash
    python main.py
    ```

2. **Follow the Prompts**:
   - Choose the tool.
   - Generate and inject G-code.
   - Simulate the overall G-code.

### Building an Executable

1. **Build the Program with PyInstaller**:
    ```bash
    pyinstaller --onefile main.py
    ```
2. **Edit the main spec**:
   - Add the hidden import and the lib folder and tools folder
 
3. **Rebuild with the main spec file**:
    ```bash
    pyinstaller main.spec
    ```
    - When prompted, press y to overwrite the build directory.
4. **Run the Executable**:
   - Navigate to the `dist` directory.
   - Run the EXE file to start the application.

### Example Usage

To inject G-code for the VacuumSuction Tool:

1. **Select the Option**: Choose to generate and inject G-code.
2. **Specify Parameters**: Enter the height where the G-code should be injected.
3. **Provide Output Path**: Specify where the modified G-code will be saved.

## Contributing

Contributions to **SupremeSlicer** are welcome! Please fork the repository and submit a pull request with your changes. Ensure that your contributions are well-documented and tested.

## Contact

For questions or support, reach out to [pralishbusiness@gmail.com](mailto:pralishbusiness@gmail.com).

Created by Pralish Satyal, 22/07/2024.
