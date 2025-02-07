#!/bin/bash

# Assign arguments to variables
RCLONE_ALIAS="$1"
UPLOADFOLDER="$2"
directory="$3"
VENDOR="$4"
FOLDERNAME="$5"
RCLONEPATH="$6"

SRC="./uploadables/$directory"
DST="$RCLONE_ALIAS:$UPLOADFOLDER/$VENDOR/$FOLDERNAME/$directory/"

# Execute rclone copy command with the specified options
$RCLONEPATH copy --stats 2s --progress --drive-acknowledge-abuse --create-empty-src-dirs --transfers 5 --stats-log-level NOTICE "$SRC" "$DST" --config ./credentials/rclone.conf --log-file ./upload.log

# Moving Successful Results to BACKUP
mv -f ./uploadables/* ./BACKUP/