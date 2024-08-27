try {
    $RCLONE_ALIAS = [string]$args[0]
    $UPLOADFOLDER = [string]$args[1]
    $directory = [string]$args[2]
    $VENDOR = [string]$args[3]
    $FOLDERNAME = [string]$args[4]
    $RCLONEPATH = [string]$args[5]

    $SRC = ".\uploadables\$directory"
    $DST = "$($RCLONE_ALIAS):$UPLOADFOLDER/$VENDOR/$FOLDERNAME/$directory/"

    & $RCLONEPATH copy --stats 2s --progress --drive-acknowledge-abuse --create-empty-src-dirs --transfers 5 --stats-log-level NOTICE $SRC $DST --config .\credentials\rclone.conf --log-file .\upload.log

    # Moving Successful Results to BACKUP
    Move-Item -Force .\uploadables\* .\BACKUP\
}
catch {
    Write-Output "`n--ERROR--$_"
}
