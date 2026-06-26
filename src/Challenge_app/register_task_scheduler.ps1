# ============================================================
# Task Scheduler Registration Script
# Run as Administrator: Right-click -> "Run with PowerShell"
# ============================================================

$TaskName  = "TaskManagerReminderChecker"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Checker   = Join-Path $ScriptDir "task_reminder_checker.py"

# Find real Python executable (sys.executable bypasses WindowsApps stub)
$PythonW = $null

$realPy = & python -c "import sys; print(sys.executable)" 2>$null
if ($realPy -and (Test-Path $realPy)) {
    $pw = Join-Path (Split-Path $realPy) "pythonw.exe"
    $PythonW = if (Test-Path $pw) { $pw } else { $realPy }
}

if (-not $PythonW) {
    Write-Host "[ERROR] Python not found. Please check your PATH." -ForegroundColor Red
    Pause; exit 1
}

Write-Host "Python  : $PythonW"
Write-Host "Script  : $Checker"
Write-Host "Task    : $TaskName"
Write-Host ""

# Remove existing task and re-register
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Remove existing task
schtasks /delete /tn $TaskName /f 2>$null | Out-Null

# Register with schtasks (no admin required for current user)
# Trigger: At logon + every 5 minutes indefinitely
$result = schtasks /create `
    /tn $TaskName `
    /tr "`"$PythonW`" `"$Checker`"" `
    /sc MINUTE `
    /mo 5 `
    /f 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Task Scheduler registration complete." -ForegroundColor Green
    Write-Host "     Checks every 5 minutes and sends desktop notifications for overdue/reminder tasks."
} else {
    Write-Host "[ERROR] Registration failed:" -ForegroundColor Red
    Write-Host $result
}

Pause
