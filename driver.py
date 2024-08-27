# Date : 2024/08/23 (YYYY/MM/DD)
# Author: Aayush Rajthala
# This script is designed to capture desktop screen & network traffic of the running machine, and place them in their respective folder in google drive using rclone.
# This script now runs in both headless and visual mode
# AKA >> Pcapture v3.6

import os
import sys
import json
import time
import shutil
import signal
import socket
import psutil
import argparse
import threading
import subprocess
from datetime import datetime
from os import path as directoryPath
from os.path import exists as checkExistence

############################################################################################
# Banner function...


def infoBanner():
    print("\n[ WEBIDENCE-STANDALONE ] Developed By Aayush Rajthala!\n")


def successBanner():
    # Test Completed ASCII ART...
    print("\n")
    print(
        "╔╦╗╔═╗╔═╗╔╦╗  ╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╔╦╗╔═╗╔╦╗\n ║ ║╣ ╚═╗ ║   ║  ║ ║║║║╠═╝║  ║╣  ║ ║╣  ║║\n ╩ ╚═╝╚═╝ ╩   ╚═╝╚═╝╩ ╩╩  ╩═╝╚═╝ ╩ ╚═╝═╩╝"
    )


infoBanner()

############################################################################################
# ENVIRONMENT FUNCTIONS & VARIABLES

STATUSCODE = ["ERROR", "INFO", "SUCCESS"]


def getFullPath(pathValue):
    return directoryPath.normpath(directoryPath.abspath(pathValue))


def getFileSize(file):
    return directoryPath.getsize(file)


def isFileEmpty(file):
    return getFileSize(file) == 0


def isWin():
    # Returns True, For Windows
    # Returns False, For Linux & Mac
    return os.name == "nt"


def clear_screen():
    if isWin():
        os.system("cls")
    else:
        os.system("clear")

    infoBanner()


def printMessage(type, message):
    colorCode = 33

    if type == "ERROR":
        colorCode = 31

    elif type == "SUCCESS":
        colorCode = 32

    else:
        type = "INFO"
        colorCode = 33

    print(f"\n--[\033[1;{colorCode}m {type} \033[0m]--[ {message} ]\n")

    return


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
rcloneConfigFilepath = getFullPath("credentials/rclone.conf")
ffmpegFilepath = getFullPath("dependencies/ffmpeg/bin/ffmpeg.exe")
tsharkFilepath = getFullPath("dependencies/wireshark/tshark.exe")

############################################################################################
# Checking Dependencies...


def checkDependencies():
    clear_screen()

    MISSING = False
    EMPTY = False

    # Define all required files
    required_files = [
        capture_script,
        directory_generation_script,
        uploader_script,
        vmInfoFilepath,
        projectInfoFilepath,
        rcloneConfigFilepath,
    ]

    # Check platform-specific dependencies
    if isWin():
        required_files.extend([ffmpegFilepath, tsharkFilepath])

    printMessage(STATUSCODE[1], "Dependencies Check")
    for file in required_files:
        if not checkExistence(getFullPath(file)):
            print(f"\033[1;31mMissing \033[0m: {file}")
            MISSING = True
        else:
            if isFileEmpty(file):
                print(f"\033[1;34mEmpty \033[0m: {file}")
                EMPTY = True
            else:
                print(f"\033[1;32mFound \033[0m: {file}")

    print("\n")

    if MISSING or EMPTY:
        exit()

    # If all files exist, return successfully
    return


checkDependencies()

############################################################################################
# Parsing ENV Data...

with open(projectInfoFilepath, "r") as envFile:
    PROJECT = json.load(envFile)

with open(vmInfoFilepath, "r") as envFile:
    vmInfoJSON = json.load(envFile)
    VMINFO = vmInfoJSON.get("VMINFO")

ENV = PROJECT.get("ENV")
RCLONE_ALIAS = ENV.get("RCLONE_ALIAS")
UPLOAD_FOLDER = ENV.get("UPLOAD_FOLDER")
ALLOWED_TESTERS = sorted(ENV.get("allowedTesters"))
TEST_INFO = ENV.get("testInfo")
TEST_CATEGORY = sorted({test.get("category") for test in TEST_INFO})
TEST_TYPES = sorted(ENV.get("testtype"))

# Parsing VENDORS Data...
VENDORS = PROJECT["VENDORS"]

# Parsing Log Paths...
access_log_path = (
    getFullPath(ENV.get("WIN_ACCESS_LOG_PATH"))
    if isWin()
    else getFullPath(ENV.get("LIN_ACCESS_LOG_PATH"))
)

error_log_path = (
    getFullPath(ENV.get("WIN_ERROR_LOG_PATH"))
    if isWin()
    else getFullPath(ENV.get("LIN_ERROR_LOG_PATH"))
)

# Default Operations...
LCAPTURE = False
PCAPTURE = True
VCAPTURE = False


############################################################################################
# FUNCTIONS DECLARATIONS...


def resetPIDs(testerID):
    fileList = os.listdir(getFullPath("PIDs"))
    fileList = [getFullPath(f"PIDs/{file}") for file in fileList if testerID in file]

    # print(fileList)

    for file in fileList:
        os.remove(file)

    return


def killWindowsProcess(pid=None, process=None):
    try:
        if pid:
            subprocess.run(["pwsh.exe", "-Command", f"Stop-Process -Id {pid} -Force"])
            print(f"Killed Process = {pid}")

        elif process:
            subprocess.run(
                ["pwsh.exe", "-Command", f"Stop-Process -Name {process} -Force"]
            )
            print(f"Killed Process = {process}")

    except Exception as error:
        print(f"Error: {error}")


def killLinuxProcess(pid=None, process=None):
    try:
        if pid:
            # Check if the process with the given PID exists
            result = subprocess.run(
                ["bash", "-c", f"ps -p {pid}"], text=True, capture_output=True
            )
            if result.returncode != 0:
                print(f"Process with PID {pid} does not exist.")
                return

            result = subprocess.run(
                ["bash", "-c", f"kill {pid}"],
                check=True,
                text=True,
                capture_output=True,
            )
            print(f"Killed PID = {pid}")

        elif process:
            # Check if the process with the given name exists
            result = subprocess.run(
                ["bash", "-c", f"pgrep {process}"], text=True, capture_output=True
            )
            if result.returncode != 0:
                print(f"No processes found with name {process}.")
                return

            result = subprocess.run(
                ["bash", "-c", f"pkill {process}"],
                check=True,
                text=True,
                capture_output=True,
            )
            print(f"Killed Process = {process}")

    except Exception as error:
        print(f"Error: {error}")


def get_interface_ip(ifname):
    import fcntl
    import struct

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(
        fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack("256s", bytes(ifname[:15], "utf-8")),
        )[20:24]
    )


def get_default_interface():
    gateways = psutil.net_if_addrs()
    for interface, addrs in gateways.items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address != "127.0.0.1":
                return interface
    return None


def get_rclone_path():
    command = "where rclone" if isWin() else "which rclone"
    try:
        result = subprocess.check_output(command, shell=True, universal_newlines=True)
        result = directoryPath.normpath(result.strip())
        return result

    except Exception as error:
        print("Error finding rclone executable.")
        return None


def isServer(ip_address):
    returnObject = None

    for VM in VMINFO:
        VMTYPE = VM.get("type")
        validServer = VMTYPE == "SERVER"

        for info in VM.get("info"):
            if ip_address in info.get("hosts"):
                returnObject = [
                    validServer,
                    VMTYPE,
                    info["operations"],
                ]
                return returnObject

    if returnObject == None:
        printMessage(STATUSCODE[0], "Device Information not found")
        exit()


def getUserInput():
    clear_screen()
    print("\nENTER TEST INFORMATION:")

    # Input loop
    while True:
        # Input for tester
        tester = input("\nInput Tester ID >>> ").strip().upper()
        if tester not in ALLOWED_TESTERS:
            print("\nInvalid Tester. Please choose from:", ", ".join(ALLOWED_TESTERS))
            exit()

        clear_screen()

        # Input for Test Category
        print(f"\nTEST CATEGORY:\n")
        for index, name in enumerate(TEST_CATEGORY, start=1):
            print(f"{index}. {name}")

        try:
            test_category_id = int(input("\nInput Test Category >>> ").strip())
            test_category_value = TEST_CATEGORY[(test_category_id - 1)]
        except Exception as error:
            printMessage(STATUSCODE[0], "Invalid Test Category")
            exit()

        if test_category_value != "FALSE-POSITIVE":
            try:
                if (
                    (test_category_value == "LAYER7-DOS")
                    or (test_category_value == "BOT-ATTACKS")
                    or (test_category_value == "APPLICATION-SCANNING-ATTACKS")
                ):

                    filterValue = ""

                    if test_category_value == "LAYER7-DOS":
                        filterValue = "LAYER7-DOS"

                    elif test_category_value == "APPLICATION-SCANNING-ATTACKS":
                        filterValue = "APPLICATION-SCANNING-ATTACKS"

                    else:
                        filterValue = "BOT-ATTACKS"

                    TEST_NAMES = next(
                        (
                            item["subtests"]
                            for item in TEST_INFO
                            if item.get("category") == filterValue
                        ),
                        None,
                    )

                else:
                    TEST_NAMES = sorted(
                        [
                            test["name"]
                            for test in TEST_INFO
                            if test["category"] == test_category_value
                        ]
                    )

                clear_screen()

            except Exception as error:
                printMessage(STATUSCODE[0], "TEST INFO PARSE ERROR")
                # print(error)
                exit()

            print(f"\nTEST NAMES:\n")
            for index, name in enumerate(TEST_NAMES, start=1):
                print(f"{index}. {name}")

            try:
                test_code_value = int(input("\nInput Test Code >>> ").strip())
                test_category = TEST_NAMES[(test_code_value - 1)]

            except Exception as error:
                printMessage(STATUSCODE[0], "Invalid Test Code")
                # print(error)
                exit()
        else:
            test_category = "FP"

        clear_screen()

        # Input for Vendor
        print(f"\nVENDOR LIST:\n")
        for index, vendor in enumerate(VENDORS, start=1):
            print(f"{index}. {vendor['name']}")

        try:
            vendorid = int(input("\nInput Vendor ID (e.g. 1, 2) >>> "))
            vendorcode = VENDORS[(vendorid - 1)]["code"]
            vendorname = VENDORS[(vendorid - 1)]["name"]

        except Exception as error:
            printMessage(STATUSCODE[0], "Invalid Vendor Selected")
            # print(error)
            exit()

        clear_screen()

        # Input for test type
        test_type = (
            input("\nInput Test Type (e.g. PRIVATE, PUBLIC, SMOKE, TEST) >>> ")
            .strip()
            .upper()
        )
        if test_type not in TEST_TYPES:
            print("\nInvalid Test Type. Please choose from:", ", ".join(TEST_TYPES))
            exit()

        clear_screen()

        try:
            # Input for batch
            batch = int(input("\nInput Batch Number (e.g. 1, 2, 3) >>> ").strip())

            if batch > 0 and batch < 10:
                batch = f"B0{batch}"
            else:
                batch = f"B{batch}"

        except Exception as error:
            printMessage(STATUSCODE[0], "Invalid Batch Number")
            # print(error)
            exit()

        clear_screen()

        try:
            # Input for iteration
            iteration = int(
                input("\nInput Iteration Number (e.g. 1, 2, 3) >>> ").strip()
            )

            if iteration > 0 and iteration < 10:
                iteration = f"I0{iteration}"
            else:
                iteration = f"I{iteration}"

        except Exception as error:
            printMessage(STATUSCODE[0], "Invalid Iteration Number")
            # print(error)
            exit()

        clear_screen()

        # Input accepted, print the information
        print("\nInformation entered:\n")
        print("Tester >>> ", tester)
        print("Vendor >>> ", vendorname)
        print("Test Category >>> ", test_category)

        print("\nTest Name >>> ", end="")
        if len(test_type) > 0:
            test_name = (
                f"{vendorcode}-{test_category}-{batch}-{iteration}-{test_type}-{tester}"
            )

        else:
            test_name = f"{vendorcode}-{test_category}-{batch}-{iteration}-{tester}"

        print(test_name)

        # To set the upload path to vendor's codename...
        vendorname = vendorcode

        # Ask if user wants to continue
        choice = input("\nDo you want to continue (yes/no)? >>> ").strip().lower()
        if choice == "yes" or choice == "y":
            return [
                vendorname,
                test_category,
                tester,
                test_name,
            ]
        else:
            clear_screen()

            printMessage(STATUSCODE[1], "TEST INFORMATION DISCARDED")
            exit()


def getCurrentDateTime():
    currentdatetime = datetime.now().strftime("%b-%d-%Y-%HH-%Mm-%Ss")
    return currentdatetime


def directoryGeneration(name, currentdatetime):
    global execution_shell

    try:
        directoryName = rf"{str(name)}_{currentdatetime}"

        subprocess.run([execution_shell, directory_generation_script, directoryName])

        return {"status": True, "name": str(directoryName)}

    except Exception as error:
        return {"status": False, "error": error}


def copyResults(directoryName):
    # Copying Results from Results to Uploadables...
    fileList = os.listdir(rf"{directoryPath.abspath(f'./results/{directoryName}/')}")

    if len(fileList) > 0:
        os.makedirs(directoryPath.abspath(rf"./uploadables/{directoryName}/"))

        for file in fileList:
            shutil.copy(
                directoryPath.abspath(rf"./results/{directoryName}/{file}"),
                directoryPath.abspath(rf"./uploadables/{directoryName}/"),
            )


def performUpload(directoryName, VENDOR, FOLDERNAME):
    global execution_shell, RCLONE_ALIAS, UPLOAD_FOLDER

    RCLONE_PATH = get_rclone_path()

    # Script Call for uploader.ps1...
    subprocess.run(
        [
            execution_shell,
            uploader_script,
            RCLONE_ALIAS,
            UPLOAD_FOLDER,
            directoryName,
            VENDOR,
            FOLDERNAME,
            RCLONE_PATH,
        ]
    )


def checkUploadStatus(directoryName, VENDOR, FOLDERNAME):
    global RCLONE_ALIAS, UPLOAD_FOLDER

    RCLONE_PATH = get_rclone_path()

    # Build the remote path
    remote_path = (
        f"{RCLONE_ALIAS}:{UPLOAD_FOLDER}/{VENDOR}/{FOLDERNAME}/{directoryName}"
    )

    # Command to check if the directory exists in the remote
    command = [RCLONE_PATH, "lsf", remote_path]

    try:
        # Execute the command and capture output
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        # If the output is empty, the directory doesn't exist; otherwise, it does
        if result.returncode == 0 and result.stdout:
            return True
        else:
            return False

    except Exception as error:
        # print(f"Error checking directory status: {error}")
        return False


def safe_terminate(process):
    """
    Terminate a process safely using psutil.
    """
    try:
        # Send SIGTERM signal
        process.terminate()

        # Wait for process to terminate
        process.wait(timeout=5)

    except psutil.TimeoutExpired:
        # If the process does not terminate, kill it
        process.kill()


def get_pid(tester):
    try:
        filename = f"PIDs/{tester}-PIDs.txt"

        with open(getFullPath(filename), "rb", buffering=0) as file:
            data = file.read()
            pidList = data.decode().splitlines()
            pidList = [value.strip() for value in pidList if len(value.strip()) > 0]

            return pidList

    except Exception as error:
        print(f"EXCEPTION IN PID = {error}")
        return None


def killProcess(tester):
    pidList = get_pid(tester)
    # print(pidList)

    if isWin():  # For Windows
        # process_names = ["ffmpeg.exe", "tshark.exe", "dumpcap.exe"]

        try:
            for pid in pidList:
                killWindowsProcess(pid=pid)

        except Exception as error:
            pass

    else:  # For Linux
        try:
            global VCAPTURE

            if VCAPTURE:
                ffmpeg_process_name = "ffmpeg"
                killLinuxProcess(process=ffmpeg_process_name)

            for pid in pidList:
                killLinuxProcess(pid=pid)

        except Exception as error:
            pass

    clear_screen()
    # resetPIDs(testerID=tester)


def watchdog():
    while True:
        global TESTER

        # Removing TESTER-stopper.txt
        if os.path.exists(f"{TESTER}-stopper.txt"):
            killProcess(TESTER)
            os.remove(f"{TESTER}-stopper.txt")
            return

        time.sleep(2)


# def signal_handler(sig, frame):
#     global TESTER

#     print("\nKeyboard Interrupt Detected! Exiting gracefully...")
#     killProcess(TESTER)
#     exit()


# Signal handler for SIGINT (Ctrl+C)
# signal.signal(signal.SIGINT, signal_handler)


############################################################################################
# DRIVER CODE...
def main():
    global TESTER, LCAPTURE, PCAPTURE, VCAPTURE

    # Getting Host Information...
    if isWin():
        HOSTNAME = socket.gethostname()
        IP_ADDRESS = socket.gethostbyname(HOSTNAME)

    else:
        interface = get_default_interface()
        if interface:
            interface_name = interface
        else:
            interface_name = "eth0"

        IP_ADDRESS = get_interface_ip(interface_name)

    ISSERVER, VMTYPE, OPERATIONS = isServer(IP_ADDRESS)

    ############################################################################################
    # GLOBAL INPUT VARIABLES...

    parser = argparse.ArgumentParser(description="WEBIDENCE")

    # Argument parser for testname, Ex:BASE-XSS-B01-I01-TEST-AR
    parser.add_argument("--testname", type=str, help="Test name")

    # Argument parser for upload status, Ex:y or yes, n or no
    parser.add_argument("--upload", type=str, help="Upload status")

    # Argument parser for operations, Ex:lvp where l = log, p = packet, v = video
    parser.add_argument("--operations", type=str, help="Operations")

    args = parser.parse_args()

    TESTNAME = args.testname
    UPLOADSTATUS = args.upload
    argOPERATIONS = args.operations

    # Validating arguments...
    if TESTNAME:
        try:
            VENDOR, FOLDERNAME = TESTNAME.split("-")[:2]
            TESTER = TESTNAME.split("-")[-1]

        except Exception as error:
            VENDOR = FOLDERNAME = TESTER = "TEST"
            pass

    else:
        VENDOR, FOLDERNAME, TESTER, TESTNAME = getUserInput()

    if UPLOADSTATUS:
        statusValue = UPLOADSTATUS.strip().lower()
        if statusValue == "y" or statusValue == "yes":
            UPLOADSTATUSVALID = 1
        if statusValue == "n" or statusValue == "no":
            UPLOADSTATUSVALID = 0

    else:
        UPLOADSTATUSVALID = -1

    if argOPERATIONS:
        OPERATIONS = argOPERATIONS.strip().lower()

    OPERATIONS_LIST = list(set(list(OPERATIONS)))

    # Confirming logging operations...
    LCAPTURE = "l" in OPERATIONS_LIST

    # Confirming packet capture operations...
    PCAPTURE = "p" in OPERATIONS_LIST

    # Confirming video capture operations...
    VCAPTURE = "v" in OPERATIONS_LIST

    clear_screen()

    try:
        currentDateTime = getCurrentDateTime()

        generationStatus = directoryGeneration(TESTNAME, currentDateTime)

        if generationStatus["status"]:

            resetPIDs(TESTER)

            # Removing stopper.txt
            stopperfilename = rf"{TESTER}-stopper.txt"

            if os.path.exists(getFullPath(stopperfilename)):
                os.remove(getFullPath(stopperfilename))

            ############################################################################################
            # WATCHDOG SERVICE...

            # Creating the watchdog thread
            watchdog_thread = threading.Thread(target=watchdog)

            # Set as daemon thread so it exits when main script exits
            watchdog_thread.daemon = True

            # Starting the watchdog thread
            watchdog_thread.start()

            ############################################################################################

            directoryName = generationStatus["name"]

            scriptArguments = [
                execution_shell,
                capture_script,
                str(directoryName),
                str(TESTNAME),
                currentDateTime,
                VMTYPE,
                TESTER,
                str(LCAPTURE),
                str(PCAPTURE),
                str(VCAPTURE),
            ]

            if LCAPTURE:
                scriptArguments.extend(
                    [
                        access_log_path,
                        error_log_path,
                    ]
                )

            # Capture Script Execution...
            subprocess.run(scriptArguments)

        else:
            print(generationStatus["error"])
            raise Exception("DIRECTORY GENERATION FAILURE")

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt Detected! Exiting gracefully...")
        killProcess(TESTER)

    except Exception as error:
        printMessage(STATUSCODE[0], error)

    finally:
        killProcess(TESTER)

        if UPLOADSTATUSVALID == 1:
            # Copying Results from Results to Uploadables...
            copyResults(directoryName)

            printMessage(STATUSCODE[1], "UPLOAD OPERATION STARTED")

            # Performing upload operation...
            performUpload(directoryName, VENDOR, FOLDERNAME)

            if checkUploadStatus(directoryName, VENDOR, FOLDERNAME):
                printMessage(STATUSCODE[2], "UPLOAD SUCCESSFUL")
            else:
                printMessage(STATUSCODE[0], "UPLOAD FAILED")

        if UPLOADSTATUSVALID == -1:
            while True:
                clear_screen()

                # Ask if user wants to upload...
                choice = input("\nDo you want to Upload (y/n)? >>> ").strip().lower()
                if choice == "yes" or choice == "y":
                    # Copying Results from Results to Uploadables...
                    copyResults(directoryName)

                    printMessage(STATUSCODE[1], "UPLOAD OPERATION STARTED")

                    # Performing upload operation...
                    performUpload(directoryName, VENDOR, FOLDERNAME)

                    if checkUploadStatus(directoryName, VENDOR, FOLDERNAME):
                        printMessage(STATUSCODE[2], "UPLOAD SUCCESSFUL")
                    else:
                        printMessage(STATUSCODE[0], "UPLOAD FAILED")

                    # Breaking Loop...
                    break

                else:
                    choice = (
                        input("\nAre you sure you don't want to upload (y/n)? >>> ")
                        .strip()
                        .lower()
                    )
                    if choice == "yes" or choice == "y":
                        break

        # Test Completed ASCII ART...
        successBanner()


if __name__ == "__main__":
    main()
