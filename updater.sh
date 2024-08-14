#!/bin/bash

# Variables
REMOTE="CTRL"
SRC="$REMOTE:TOOLS/webidence/"
DEST="/home/ubuntu/TOOLS/webidence/"
LOG_FILE="/home/ubuntu/TOOLS/rclone.log"

# rclone command
rclone copy --stats 5s --stats-log-level NOTICE --create-empty-src-dirs --transfers 20 "$SRC" "$DEST" --log-file "$LOG_FILE"
