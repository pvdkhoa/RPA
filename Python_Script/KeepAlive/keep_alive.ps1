Add-Type -AssemblyName System.Windows.Forms
while ($true) {
    # Lấy vị trí chuột hiện tại
    $pos = [System.Windows.Forms.Cursor]::Position

    # Random: -1 = qua trái, 1 = qua phải
    $direction = Get-Random -InputObject @(-1, 1)

    # Tính vị trí mới
    $newX = $pos.X + ($direction * $moveAmount)
    $newY = $pos.Y

    # Di chuyển chuột
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($newX, $newY)

    # Chờ 60 giây rồi lặp lại
    Start-Sleep -Seconds 60
}