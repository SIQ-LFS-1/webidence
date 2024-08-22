import os
import sys
import importlib
import subprocess
from datetime import datetime
from os import path as directoryPath
from os.path import exists as checkExistence

############################################################################################
# ENVIRONMENT FUNCTIONS & VARIABLES

STATUSCODE = ["ERROR", "INFO", "SUCCESS"]


def getFullPath(pathValue):
    return directoryPath.normpath(directoryPath.abspath(pathValue))


def isWin():
    # Returns True, For Windows
    # Returns False, For Linux & Mac
    return os.name == "nt"


def clear_screen():
    if isWin():
        os.system("cls")
    else:
        os.system("clear")


def printMessage(type, message):
    colorCode = 33

    if type == "ERROR":
        colorCode = 31

    elif type == "SUCCESS":
        colorCode = 32

    else:
        type = "INFO"
        colorCode = 33

    print(f"--[\033[1;{colorCode}m {type} \033[0m]--[ {message} ]\n")

    return


############################################################################################
# Function to Check and Install Missing Libraries


def check_and_install_libraries(required_libraries):
    for library in required_libraries:
        try:
            # Attempt to import the library
            importlib.import_module(library)
        except ImportError:
            printMessage(STATUSCODE[0], f"Library '{library}' not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", library])


required_libraries = ["psutil", "python-dotenv"]

# Run the library check
check_and_install_libraries(required_libraries)

############################################################################################
# Loading Script Paths based on OS...

if isWin():
    execution_shell = "pwsh.exe"
    capture_script = getFullPath("scripts/capture.ps1")
    uploader_script = getFullPath("scripts/uploader.ps1")
    directory_generation_script = getFullPath("scripts/directorygeneration.ps1")

else:
    execution_shell = "bash"
    capture_script = getFullPath("scripts/capture.sh")
    uploader_script = getFullPath("scripts/uploader.sh")
    directory_generation_script = getFullPath("scripts/directorygeneration.sh")

vmInfoFilepath = getFullPath("credentials/vmInfo.json")
projectInfoFilepath = getFullPath("credentials/projectInfo.json")
ffmpegFilepath = getFullPath("dependencies/ffmpeg/bin/ffmpeg.exe")
tsharkFilepath = getFullPath("dependencies/wireshark/tshark.exe")


############################################################################################
# Checking Dependencies...


def checkDependencies():
    clear_screen()

    # Define all required files
    required_files = [
        capture_script,
        directory_generation_script,
        uploader_script,
        vmInfoFilepath,
        projectInfoFilepath,
    ]

    # Check platform-specific dependencies
    if isWin():
        required_files.extend([ffmpegFilepath, tsharkFilepath])

    printMessage(STATUSCODE[1], "Dependencies Check")
    for file in required_files:
        if not checkExistence(getFullPath(file)):
            print(f"\033[1;31mMissing\033[0m: {file}")
        else:
            print(f"\033[1;32mFound \033[0m: {file}")

    # If all files exist, return successfully
    return


checkDependencies()