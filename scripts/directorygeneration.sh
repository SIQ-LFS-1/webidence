#!/bin/bash

directoryName=$1

# Directory Generation...
if [ ! -d "./results" ]; then
    mkdir "./results"
fi

if [ ! -d "./uploadables" ]; then
    mkdir "./uploadables"
fi

if [ ! -d "./BACKUP" ]; then
    mkdir "./BACKUP"
fi

if [ ! -d "./PIDs" ]; then
    mkdir "./PIDs"
fi

if [ ! -d "./results/$directoryName" ]; then
    mkdir "./results/$directoryName"
fi

# Uncomment if needed
# if [ ! -d "./uploadables/$directoryName" ]; then
#     mkdir "./uploadables/$directoryName"
# fi
