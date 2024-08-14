#!/bin/bash

directoryName=$1
testName=$2
currentDateTime=$3
VMTYPE=$4
TESTER=$5
LCAPTURE=$6
PCAPTURE=$7
VCAPTURE=$8

logDir="./results/$directoryName"
pidDir="./PIDs"

log_start="------------------- Test Log Starts @ $(date '+%b-%d-%Y-%H-%M-%S') -----------------------"

# Driver Code...
{
    echo "----------[ LOG/SCREEN/PCAP CAPTURE TOOL ]----------"

    if [ "$LCAPTURE" == "True" ]; then
        ACCESSLOGPATH=$9
        ERRORLOGPATH=${10}

        accessLogPath="$logDir/${testName}-${VMTYPE}-ACCESS_${currentDateTime}-PST.log"
        errorLogPath="$logDir/${testName}-${VMTYPE}-ERROR_${currentDateTime}-PST.log"

        echo "$log_start" >> "$accessLogPath"
        echo "$log_start" >> "$errorLogPath"

        # Create log files if they don't exist
        touch "$accessLogPath"
        touch "$errorLogPath"

        if [ "$PCAPTURE" != "True" ] && [ "$VCAPTURE" != "True" ]; then
            tail -f "$ACCESSLOGPATH" >> "$accessLogPath" &
            access_pid=$!
            echo $access_pid >> "$pidDir/${TESTER}-PIDs.txt"

            tail -f "$ERRORLOGPATH" >> "$errorLogPath" &
            error_pid=$!
            echo $error_pid >> "$pidDir/${TESTER}-PIDs.txt"

            echo "--OPERATION--Log Capture Operation Started!"

            wait $access_pid $error_pid
        else
            tail -f "$ACCESSLOGPATH" >> "$accessLogPath" &
            access_pid=$!
            echo $access_pid >> "$pidDir/${TESTER}-PIDs.txt"

            tail -f "$ERRORLOGPATH" >> "$errorLogPath" &
            error_pid=$!
            echo $error_pid >> "$pidDir/${TESTER}-PIDs.txt"

            echo "--OPERATION--Log Capture Operation Started!"
        fi
    fi

    if [ "$PCAPTURE" == "True" ]; then
        pcapFilePath="$logDir/${testName}-${VMTYPE}-TRAFFIC_${currentDateTime}-PST.pcap"

        if [ "$VCAPTURE" != "True" ]; then
            tshark -i any -f "not port 22 and not port 3389" -q -w "$pcapFilePath" &
            
            tshark_id=$!
            echo $tshark_id >> "$pidDir/${TESTER}-PIDs.txt"

            echo "--OPERATION--Packet Capture Operation Started!"

            wait $tshark_id
        else
            tshark -i any -f "not port 22 and not port 3389" -q -w "$pcapFilePath" &
            
            tshark_id=$!
            echo $tshark_id >> "$pidDir/${TESTER}-PIDs.txt"
        
            echo "--OPERATION--Packet Capture Operation Started!"
        fi

    fi

    if [ "$VCAPTURE" == "True" ]; then
        recordingPath="$logDir/${testName}-${VMTYPE}-VIDEO_${currentDateTime}-PST.ts"

        echo "--OPERATION--Screen Record Operation Started!"
        echo "--INFO--[ PRESS Q TO STOP RECORDING ]"

        ffmpeg -f x11grab -i :0.0 -framerate 24 -loglevel error -c:v libx264 -preset fast "$recordingPath"

        echo "--OPERATION--Stopping Capture Operation!"
        echo "--OPERATION--Screen Record Operation Stopped!"
    fi
} || {
    echo "--ERROR--An error occurred during execution"
}
