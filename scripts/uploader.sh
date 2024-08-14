#!/bin/bash

RCLONE_ALIAS=$1
UPLOADFOLDER=$2
directory=$3
VENDOR=$4
FOLDERNAME=$5
RCLONEPATH=$6

echo -e "\n--[ INFO ]--[ OPERATION--UPLOAD OPERATION STARTED ]\n"

$RCLONEPATH copy --stats 2s --progress --drive-acknowledge-abuse --create-empty-src-dirs --transfers 5 --stats-log-level NOTICE "./uploadables/$directory" "$RCLONE_ALIAS:$UPLOADFOLDER/$VENDOR/$FOLDERNAME/" --config ./credentials/rclone.conf --log-file "./rclone.log"

echo -e "\n--[ RESULT ]--[ UPLOAD OPERATION COMPLETED ]"

# Moving Successful Results to BACKUP
mv -f ./uploadables/* ./BACKUP/
