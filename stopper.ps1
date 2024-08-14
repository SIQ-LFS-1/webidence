$tester = $args[0]

# Stopper File Generation...
if (!(Test-Path -Path ".\$tester-stopper.txt")) {
    New-Item ".\$tester-stopper.txt" | Out-Null
}
