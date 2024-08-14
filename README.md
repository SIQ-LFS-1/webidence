# WEBIDENCE POC - Standalone

Gitlab Link : https://gitlab.vairav.net/siq/webidence.git

## Table of Contents
- [WEBIDENCE POC - Standalone](#webidence-poc---standalone)
  - [Table of Contents](#table-of-contents)
  - [1. Introduction](#1-introduction)
  - [2. Purpose of the Tool](#2-purpose-of-the-tool)
  - [3. Environment](#3-environment)
    - [Example `projectInfo.json` File](#example-projectinfojson-file)
    - [Example `vmInfo.json` File](#example-vminfojson-file)
    - [Example `rclone.conf` File](#example-rcloneconf-file)
  - [4. Environment Requirements](#4-environment-requirements)
  - [5. Technologies Used / Dependencies](#5-technologies-used--dependencies)
  - [6. Usage](#6-usage)
    - [Using Arguments](#using-arguments)
    - [Without Arguments](#without-arguments)
  - [7. Workflow](#7-workflow)
  - [8. Execution Flow](#8-execution-flow)
  - [9. Additional Notes](#9-additional-notes)

## 1. Introduction
Webidence is a comprehensive tool designed to capture desktop screens, network traffic, and logs on a running machine. It organizes the captured data and uploads it to a storage space via rclone.

## 2. Purpose of the Tool
The primary purpose of this tool is to facilitate automated and efficient data capture (screen, network traffic, and logs) during various tests and operations on both Windows and Linux environments. It then organizes the data into structured directories and uploads them to a designated cloud storage for further analysis.

## 3. Environment
The tool is designed to run on both Windows and Linux environments. It automatically detects the operating system and adjusts its operations accordingly. Ensure the “credentials/projectInfo.json”, “credentials/vmInfo.json”, “credentials/rclone.conf”, “credentials/agent.json” files are correctly configured with the necessary project and VM information.

The agent.json file is the OAuth file provided by Google for API Access to Google services. The agent.json file is used by rclone to perform transfer operations to Google Drive.

### Example `projectInfo.json` File
```json
{
  "ENV": {
    "RCLONE_ALIAS": "Your_Rclone_Alias",
    "UPLOAD_FOLDER": "Your_Upload_Folder",
    "WIN_ACCESS_LOG_PATH": "Windows_Server_Access_Log_Path",
    "WIN_ERROR_LOG_PATH": "Windows_Server_Error_Log_Path",
    "LIN_ACCESS_LOG_PATH": "Linux_Server_Access_Log_Path",
    "LIN_ERROR_LOG_PATH": "Linux_Server_Error_Log_Path",
    "allowedTesters": [
      "Tester_1",
      "Tester_2",
      "Tester_3"
    ],
    "testInfo": [
      { "id": "Test_ID_1", "category": "Category_1", "name": "Test_Name_1" },
      { "id": "Test_ID_2", "category": "Category_2", "name": "Test_Name_2" },
      { "id": "Test_ID_3", "category": "Category_3", "name": "Test_Name_3" }
    ],
    "batches": ["1", "2", "3"],
    "iterations": ["1", "2", "3"],
    "testtype": ["PRIVATE", "PUBLIC", "SMOKE", "TEST"]
  },
  "VENDORS": [
    { "code": "Vendor_Code_1", "name": "Vendor_Name_1" },
    { "code": "Vendor_Code_2", "name": "Vendor_Name_2" },
    { "code": "Vendor_Code_3", "name": "Vendor_Name_3" }
  ]
}

```

### Example `vmInfo.json` File
```json
{
  "PATHINFO": {
    "WIN_SCRIPT_PATH": "Windows_Script_Path_For_Webidence",
    "LIN_SCRIPT_PATH": "Linux_Script_Path_For_Webidence"
  },
  "TESTERINFO": [
    { "tester": "Tester_1", "hosts": ["Host_IP_1", "Host_IP_2"] },
    {"tester": "Tester_2", "hosts": ["Host_IP_3", "Host_IP_4"] }
    ],
  "VMINFO": [
    {
      "type": "SERVER",
      "info": [
        {
          "os": "windows",
          "operations": "lp",
          "hosts": ["PUBLIC_IP_1", "PUBLIC_IP_2", "PRIVATE_IP_1","PRIVATE_IP_2"]
        },
        {
          "os": "linux",
          "operations": "lp",
          "hosts": ["PUBLIC_IP_3", "PUBLIC_IP_4", "PRIVATE_IP_3","PRIVATE_IP_4"]
        }
      ]
    },
    {
      "type": "ATTACKER",
      "info": [
        {
          "os": "windows",
          "operations": "pv",
          "hosts": ["PRIVATE_IP_5", "PRIVATE_IP_6"]
        },
        {
          "os": "linux",
          "operations": "p",
          "hosts": ["PRIVATE_IP_7", "PRIVATE_IP_8"]
        }
      ]
    }
  ]
}
```

### Example `rclone.conf` File
```bash
[Your_Remote_Name]
type = drive
client_id = Your_Client_ID
scope = drive
service_account_file = Your_Service_Account_File_Path
team_drive = Your_Team_Drive_ID
root_folder_id = Your_Root_Folder_ID
```

## 4. Environment Requirements
- Operating System: Windows or Linux
- Installed Applications:
	-  `rclone` for cloud storage operations
	-  `psutil` for process management
	-  `tshark` for network packet capturing
	-  `ffmpeg` for screen capturing
	-  `PowerShell 7` (for Windows)
	-  `Bash` (for Linux)

## 5. Technologies Used / Dependencies
- Python 3.12: Core language for the script
- PowerShell/Bash: Shell scripts for Windows/Linux operations
- rclone: Tool for file syncing to Google Drive
- tshark: Tool for network packet capturing
- ffmpeg: Tool for screen capturing
- psutil: Library for process management
- JSON configuration files for project and VM information

Note: The python libraries can be installed using the following command.

```bash
pip  install  -r  requirements.txt
```

## 6. Usage

### Using Arguments

The tool can be run with the following arguments:
-  `--testname`: Specifies the test name. Example: "BASE-XSS-B01-I01-TEST-AR"
-  `--upload`: Specifies whether to upload the results (`yes or y` OR `no or n`).
-  `--operations`: Specifies the operations to perform (`lvp`, where `l` stands for log, `v` stands for video, and `p` stands for packet).

Example:
```bash
python  driver.py  --testname  "DEV-TEST-B01-I01-TEST-AR"  --upload  "yes"  --operations  "lvp"
```

Note: These arguments override the tool’s logic and are set for explicit usage of the tool as per the user’s requirements. These arguments can be selectively used as well. The "--operations" argument takes any combination of "lvp" value for example [ "l", "v", "p", "lv", "vp", "lp", "lpv" ]

### Without Arguments
If no arguments are provided, the tool will prompt the user for the necessary information through a series of inputs.

## 7. Workflow
1. Initialization:
	- Display banners and load environment paths based on OS.
	- Check dependencies.
2. Parse Environment Data:
	- Load project and VM information from JSON files.
3. Get User Input (if no arguments provided):
	- Collect tester ID, test category, vendor, test type, batch number, and iteration number.
4. Generate Directory:
	- Create a directory for storing results.
5. Perform Operations:
	- Capture logs, packets, and/or screen based on specified operations.
6. Upload Results (if specified):
	- Copy results to the uploadable directory and perform upload using `rclone`.

## 8. Execution Flow
1. Check Dependencies: Ensure all necessary files and executables are present.
2. Parse Configuration: Read project and VM information from JSON files.
3. User Input: If arguments are not provided, prompt the user for input.
4. Directory Generation: Create a directory for storing the results of the operations.
5. Capture Operations: Based on the specified operations (`lvp`), capture logs, packets, and/or screen.
6. Upload Results: If upload is specified, copy the results to the upload directory and perform the upload using `rclone`.
7. Cleanup: Ensure all processes are terminated and resources are cleaned up.

## 9. Additional Notes
- Ensure that all dependencies are correctly installed and paths are set appropriately.
- The tool is designed to handle interruptions gracefully, ensuring all processes are terminated properly.
- The tool supports both interactive and non-interactive (argument-based) modes for flexibility.


