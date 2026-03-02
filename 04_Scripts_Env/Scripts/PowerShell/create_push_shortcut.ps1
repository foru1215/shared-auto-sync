$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\push.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File C:\Users\0190\shared\04_Scripts_Env\Scripts\PowerShell\push.ps1"
$Shortcut.WorkingDirectory = "C:\Users\0190\shared"
$Shortcut.IconLocation = "powershell.exe,0"
$Shortcut.Description = "GitHubに保存"
$Shortcut.Save()
Write-Host "デスクトップにショートカットを作成しました！" -ForegroundColor Green