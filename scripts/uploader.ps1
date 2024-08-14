try {
    $RCLONE_ALIAS = [string]$args[0]
    $UPLOADFOLDER = [string]$args[1]
    $directory = [string]$args[2]
    $VENDOR = [string]$args[3]
    $FOLDERNAME = [string]$args[4]
    $RCLONEPATH = [string]$args[5]

    Write-Output "`n--[ INFO ]--[ OPERATION--UPLOAD OPERATION STARTED ]`n"

    & $RCLONEPATH copy --stats 2s --progress --drive-acknowledge-abuse --create-empty-src-dirs --transfers 5 --stats-log-level NOTICE ".\uploadables\$directory\" "$($RCLONE_ALIAS):$UPLOADFOLDER/$VENDOR/$FOLDERNAME/" --config .\credentials\rclone.conf --log-file .\rclone.log

    Write-Output "`n--[ RESULT ]--[ UPLOAD OPERATION COMPLETED ]"

    # Moving Successful Results to BACKUP
    Move-Item -Force .\uploadables\* .\BACKUP\
}
catch {
    Write-Output "`n--ERROR--$_"
}
