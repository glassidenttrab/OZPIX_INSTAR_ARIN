# 인스타그램 서비스 중단 스크립트 (Windows PowerShell)

Write-Host "🛑 아린 인스타그램 서비스를 중단합니다..." -ForegroundColor Yellow

$scripts = @("service_monitor.py", "arin_master.py", "interaction_scheduler.py")

$found = $false
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | ForEach-Object {
    $proc = $_
    foreach ($s in $scripts) {
        if ($proc.CommandLine -like "*$s*") {
            try {
                Stop-Process -Id $proc.ProcessId -Force
                Write-Host "✅ 종료됨 (PID: $($proc.ProcessId)): $s" -ForegroundColor Green
                $found = $true
            } catch {
                Write-Host "❌ 종료 실패 (PID: $($proc.ProcessId)): $s" -ForegroundColor Red
            }
        }
    }
}

if (-not $found) {
    Write-Host "🔍 실행 중인 서비스를 찾지 못했습니다." -ForegroundColor Gray
}

# 잠금 파일 제거 (필요 시)
if (Test-Path "reports/arin_master.lock") {
    Remove-Item "reports/arin_master.lock" -Force
    Write-Host "🗑️ 잠금 파일(reports/arin_master.lock)을 제거했습니다." -ForegroundColor Gray
}

Write-Host "✨ 모든 서비스가 중단되었습니다." -ForegroundColor Cyan
