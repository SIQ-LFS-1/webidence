# Variables
$remote = "CTRL"
$src = "$($remote):TOOLS/webidence/"
$dest = "C:\Users\secureiqlab\Desktop\webidence\"
$logFile = "C:\Users\secureiqlab\Desktop\rclone.log"

# rclone command to copy .git folder...
rclone copy --stats 5s --stats-log-level NOTICE --create-empty-src-dirs --ignore-times --transfers 20 "$src/.git" "$dest/.git" --log-file "$logFile"

# rclone command to copy the complete code...
rclone copy --stats 5s --stats-log-level NOTICE --create-empty-src-dirs --ignore-times --transfers 20 "$src" "$dest" --log-file "$logFile" --include "*"

# Git stash command to get .gitignore files...
git stash | Out-Null