#!/bin/bash

# Variables
REMOTE="CTRL"
SRC="$REMOTE:TOOLS/webidence/"
DEST="/home/ubuntu/TOOLS/webidence/"
LOG_FILE="/home/ubuntu/TOOLS/rclone.log"

# rclone command to copy .git folder...
rclone copy --stats 5s --stats-log-level NOTICE --create-empty-src-dirs --ignore-times --transfers 20 "$SRC/.git" "$DEST/.git" --log-file "$LOG_FILE"

# Git stash command to get .gitignore files...
git stash > /dev/null 2>&1

# rclone command to copy the complete code...
rclone copy --stats 5s --stats-log-level NOTICE --create-empty-src-dirs --ignore-times --transfers 20 "$SRC" "$DEST" --log-file "$LOG_FILE" --include "*"