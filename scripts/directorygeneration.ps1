$directoryName = $args[0]

# Directory Generation...
if (!(Test-Path -Path ".\results")) {
    New-Item ".\results" -itemType Directory | Out-Null
}

if (!(Test-Path -Path ".\uploadables")) {
    New-Item ".\uploadables" -itemType Directory | Out-Null
}

if (!(Test-Path -Path ".\BACKUP")) {
    New-Item ".\BACKUP" -itemType Directory | Out-Null
}

if (!(Test-Path -Path ".\PIDs")) {
    New-Item ".\PIDs" -itemType Directory | Out-Null
}

if (!(Test-Path -Path ".\results\$directoryName")) {
    New-Item ".\results\$directoryName" -itemType Directory | Out-Null
}

# if (!(Test-Path -Path ".\uploadables\$directoryName")) {
#     New-Item ".\uploadables\$directoryName" -itemType Directory | Out-Null
# }