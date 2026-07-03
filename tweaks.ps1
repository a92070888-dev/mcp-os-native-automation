# Windows Desktop Automation Speed Tweaks
# Run as Administrator: powershell -ExecutionPolicy Bypass -File tweaks.ps1

Write-Host "=== Windows Desktop Automation Speed Tweaks ===" -ForegroundColor Cyan
Write-Host "Target: eliminate UI animation delays for sub-ms SendInput operations"
Write-Host ""

# 1. MenuShowDelay = 0 — eliminates 400ms hover delay on menus
$path = "HKCU:\Control Panel\Desktop"
$current = Get-ItemProperty -Path $path -Name "MenuShowDelay" -ErrorAction SilentlyContinue
if ($current.MenuShowDelay -ne 0) {
    Set-ItemProperty -Path $path -Name "MenuShowDelay" -Value 0 -Type DWord
    Write-Host "  [OK] MenuShowDelay -> 0" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] MenuShowDelay already 0" -ForegroundColor Gray
}

# 2. Disable visual feedback animations (fade/slide)
# Bitmask: bit 1=fade animation, bit 3=slide animation
# Setting to 0x9E,0x3E,0x07,0x80,0x10,0x00,0x00,0x00 = no animations + high perf
$current = Get-ItemProperty -Path $path -Name "UserPreferencesMask" -ErrorAction SilentlyContinue
$targetMask = [byte[]]@(0x9E, 0x3E, 0x07, 0x80, 0x10, 0x00, 0x00, 0x00)
if ($current.UserPreferencesMask) {
    $changed = $false
    for ($i = 0; $i -lt [Math]::Min($targetMask.Length, $current.UserPreferencesMask.Length); $i++) {
        if ($current.UserPreferencesMask[$i] -ne $targetMask[$i]) { $changed = $true; break }
    }
    if ($changed) {
        Set-ItemProperty -Path $path -Name "UserPreferencesMask" -Value $targetMask -Type Binary
        Write-Host "  [OK] UserPreferencesMask updated (animations OFF)" -ForegroundColor Green
    } else {
        Write-Host "  [SKIP] UserPreferencesMask already optimal" -ForegroundColor Gray
    }
} else {
    Set-ItemProperty -Path $path -Name "UserPreferencesMask" -Value $targetMask -Type Binary
    Write-Host "  [OK] UserPreferencesMask set (animations OFF)" -ForegroundColor Green
}

# 3. Disable window minimize/maximize animation
Set-ItemProperty -Path "$path\WindowMetrics" -Name "MinAnimate" -Value 0 -Type DWord
Write-Host "  [OK] MinAnimate -> 0" -ForegroundColor Green

# 4. Disable ComboBox animation + taskbar animations
$advPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
Set-ItemProperty -Path $advPath -Name "ComboBoxAnimation" -Value 0 -Type DWord
Set-ItemProperty -Path $advPath -Name "TaskbarAnimations" -Value 0 -Type DWord
Set-ItemProperty -Path $advPath -Name "EnableWindowAnimations" -Value 0 -Type DWord
Write-Host "  [OK] Explorer animations disabled" -ForegroundColor Green

# 5. Reduce mouse hover activation time
$mousePath = "HKCU:\Control Panel\Mouse"
Set-ItemProperty -Path $mousePath -Name "MouseHoverTime" -Value 100 -Type DWord
Write-Host "  [OK] MouseHoverTime -> 100ms" -ForegroundColor Green

# 6. Disable cursor shadow (tiny perf gain, but every bit counts)
$cursorPath = "HKCU:\Control Panel\Cursors"
Set-ItemProperty -Path $cursorPath -Name "CursorShadow" -Value 0 -Type DWord -ErrorAction SilentlyContinue
Write-Host "  [OK] CursorShadow -> 0" -ForegroundColor Green

# 7. Disable font smoothing animation (ClearType still on, just animation off)
$fontPath = "HKCU:\Control Panel\Desktop"
Set-ItemProperty -Path $fontPath -Name "FontSmoothing" -Value 2 -Type String  # 2=ClearType, no animation
Write-Host "  [OK] FontSmoothing confirmation" -ForegroundColor Green

Write-Host ""
Write-Host "  SUMMARY: 7 tweaks applied." -ForegroundColor Cyan
Write-Host "  REBOOT REQUIRED for all changes to take effect." -ForegroundColor Yellow
Write-Host ""
Write-Host "  After reboot, run the benchmark again:" -ForegroundColor Gray
Write-Host "    cd C:\Users\PP\os-native-mcp" -ForegroundColor Gray
Write-Host "    python os_native_ultraclick.py --benchmark" -ForegroundColor Gray
Write-Host ""

# Optionally trigger reboot
$choice = Read-Host "  Reboot now? (y/N)"
if ($choice -eq "y" -or $choice -eq "Y") {
    Write-Host "  Rebooting in 5 seconds..." -ForegroundColor Red
    Start-Sleep -Seconds 5
    Restart-Computer -Force
}
