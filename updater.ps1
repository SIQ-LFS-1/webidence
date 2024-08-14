# Variables
$remote = "CTRL"
$src = "$($remote):TOOLS/webidence/"
$dest = "C:\Users\secureiqlab\Desktop\webidence\"
$logFile = "C:\Users\secureiqlab\Desktop\rclone.log"

# rclone command
rclone copy --stats 5s --stats-log-level NOTICE --create-empty-src-dirs --transfers 20 "$src" "$dest" --log-file "$logFile"