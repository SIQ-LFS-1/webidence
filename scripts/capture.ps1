$directoryName = $args[0]
$testName = $args[1]
$currentDateTime = $args[2]
$VMTYPE = $args[3]
$TESTER = $args[4]
$LCAPTURE = ($args[5] -eq "True")
$PCAPTURE = ($args[6] -eq "True")
$VCAPTURE = ($args[7] -eq "True")


# Driver Code...
try {
    Write-Output "----------[ LOG/SCREEN/PCAP CAPTURE TOOL ]----------`n"

    if ($LCAPTURE) {
        $ACCESSLOGPATH = [string]$args[8]
        $ERRORLOGPATH = [string]$args[9]
    
        $now = Get-Date -Format "MMM-dd-yyyy-HH-mm-ss"
        $log_start = "------------------- Test Log Starts @ $now -----------------------"
    
        # Start capturing logs
        Add-Content -Path ".\results\$directoryName\$testName-$VMTYPE-ACCESS_$currentDateTime-PST.log" -Value "$log_start`n"
        Add-Content -Path ".\results\$directoryName\$testName-$VMTYPE-ERROR_$currentDateTime-PST.log" -Value "$log_start`n"
    
        if (!($PCAPTURE) -and !($VCAPTURE)) {
            # Start capturing the access log and get the process object
            $accessProcess = Start-Process pwsh.exe -ArgumentList "-NoProfile -Command Get-Content -Path $ACCESSLOGPATH -Wait | Out-File -Append '.\results\$directoryName\$testName-SERVER-ACCESS_$currentDateTime-PST.log'" -NoNewWindow -PassThru
            $access_pid = $accessProcess.Id
        
            # Start capturing the error log and get the process object
            $errorProcess = Start-Process pwsh.exe -ArgumentList "-NoProfile -Command Get-Content -Path $ERRORLOGPATH -Wait | Out-File -Append '.\results\$directoryName\$testName-SERVER-ERROR_$currentDateTime-PST.log'" -NoNewWindow -PassThru
            $error_pid = $errorProcess.Id
            
            Add-Content -Path ".\PIDs\$tester-PIDs.txt" -Value "$access_pid`n$error_pid"
    
            # Wait for both processes to complete
            Wait-Process -Id $access_pid
            Wait-Process -Id $error_pid
        }
        else {
            # Start capturing the access log and get the process object
            $accessProcess = Start-Process pwsh.exe -ArgumentList "-NoProfile -Command Get-Content -Path $ACCESSLOGPATH -Wait | Out-File -Append '.\results\$directoryName\$testName-SERVER-ACCESS_$currentDateTime-PST.log'" -NoNewWindow -PassThru
            $access_pid = $accessProcess.Id
        
            # Start capturing the error log and get the process object
            $errorProcess = Start-Process pwsh.exe -ArgumentList "-NoProfile -Command Get-Content -Path $ERRORLOGPATH -Wait | Out-File -Append '.\results\$directoryName\$testName-SERVER-ERROR_$currentDateTime-PST.log'" -NoNewWindow -PassThru
            $error_pid = $errorProcess.Id
    
            Add-Content -Path ".\PIDs\$tester-PIDs.txt" -Value "$access_pid`n$error_pid"
        }
    }

    if ($PCAPTURE) {
        $pcapFilePath = ".\results\$directoryName\$testName-$VMTYPE-TRAFFIC_$currentDateTime-PST.pcap"
        
        # Invoke Packet Capture Operation...
        if (!($VCAPTURE)) {
            Write-Output "`n--OPERATION--Packet Capture Operation Started!"
            $pcapProcess = Start-Process -FilePath .\dependencies\wireshark\tshark.exe -ArgumentList "-i TRAFFIC -f `"not(port 22 or port 3389)`" -q -w $pcapFilePath" -NoNewWindow -PassThru
            $pcap_pid = $pcapProcess.Id

            Add-Content -Path ".\PIDs\$tester-PIDs.txt" -Value "$pcap_pid`n"

            Wait-Process -Id $pcap_pid
        }
        else {
            $pcapProcess = Start-Process -FilePath .\dependencies\wireshark\tshark.exe -ArgumentList "-i TRAFFIC -f `"not(port 22 or port 3389)`" -q -w $pcapFilePath" -NoNewWindow -PassThru
            $pcap_pid = $pcapProcess.Id

            Add-Content -Path ".\PIDs\$tester-PIDs.txt" -Value "$pcap_pid`n"
            
            Write-Output "`n--OPERATION--Packet Capture Operation Started!"
        }
    }
    
    if ($VCAPTURE) {
        $recordingPath = ".\results\$directoryName\$testName-$VMTYPE-VIDEO_$currentDateTime-PST.ts"
        
        Write-Output "--OPERATION--Screen Record Operation Started!"
        Write-Output "`n--INFO--[ PRESS Q TO STOP RECORDING ]`n"
        
        # Invoke Screen Recording Operation...
        $ffmpegProcess = Start-Process -FilePath .\dependencies\ffmpeg\bin\ffmpeg.exe -ArgumentList "-f gdigrab -i desktop -framerate 24 -loglevel error -c:v libx264 -preset fast $recordingPath" -NoNewWindow -PassThru
        $ffmpeg_pid = $ffmpegProcess.Id
        
        Add-Content -Path ".\PIDs\$tester-PIDs.txt" -Value "$ffmpeg_pid`n"
        
        Wait-Process -Id $ffmpeg_pid

        Write-Output "--OPERATION--Stopping Capture Operation!"
        Write-Output "--OPERATION--Screen Record Operation Stopped!"
    }
}
catch [System.Exception] {
    Write-Output "`n--ERROR--$_.Exception.Message"
}
