#!/bin/bash

tester=$1

# Stopper File Generation...
if [ ! -f "./$tester-stopper.txt" ]; then
    touch "./$tester-stopper.txt"
fi
