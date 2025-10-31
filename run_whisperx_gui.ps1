Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# === GUI SETUP ===
$form = New-Object System.Windows.Forms.Form
$form.Text = "WhisperX GUI"
$form.Width = 520
$form.Height = 330
$form.StartPosition = "CenterScreen"

# Input file selector
$lblInput = New-Object System.Windows.Forms.Label
$lblInput.Text = "Select input file:"
$lblInput.AutoSize = $true
$lblInput.Top = 20
$lblInput.Left = 10
$form.Controls.Add($lblInput)

$txtInput = New-Object System.Windows.Forms.TextBox
$txtInput.Width = 360
$txtInput.Top = 40
$txtInput.Left = 10
$form.Controls.Add($txtInput)

$btnBrowse = New-Object System.Windows.Forms.Button
$btnBrowse.Text = "Browse..."
$btnBrowse.Top = 38
$btnBrowse.Left = 380
$btnBrowse.Width = 100
$form.Controls.Add($btnBrowse)

# Language input
$lblLang = New-Object System.Windows.Forms.Label
$lblLang.Text = "Language (default: nl):"
$lblLang.AutoSize = $true
$lblLang.Top = 80
$lblLang.Left = 10
$form.Controls.Add($lblLang)

$txtLang = New-Object System.Windows.Forms.TextBox
$txtLang.Width = 100
$txtLang.Top = 100
$txtLang.Left = 10
$txtLang.Text = "nl"
$form.Controls.Add($txtLang)

# Timestamp input
$lblTimestamp = New-Object System.Windows.Forms.Label
$lblTimestamp.Text = "Timestamp (hh:mm:ss) (optional):"
$lblTimestamp.AutoSize = $true
$lblTimestamp.Top = 140
$lblTimestamp.Left = 10
$form.Controls.Add($lblTimestamp)

$txtTimestamp = New-Object System.Windows.Forms.TextBox
$txtTimestamp.Width = 120
$txtTimestamp.Top = 160
$txtTimestamp.Left = 10
$form.Controls.Add($txtTimestamp)

# Start button
$btnRun = New-Object System.Windows.Forms.Button
$btnRun.Text = "Start WhisperX"
$btnRun.Top = 200
$btnRun.Left = 10
$btnRun.Width = 150
$form.Controls.Add($btnRun)

# Output box
$txtOutput = New-Object System.Windows.Forms.TextBox
$txtOutput.Multiline = $true
$txtOutput.Width = 470
$txtOutput.Height = 70
$txtOutput.Top = 240
$txtOutput.Left = 10
$txtOutput.ReadOnly = $true
$form.Controls.Add($txtOutput)

# === EVENTS ===
$btnBrowse.Add_Click({
    $dialog = New-Object System.Windows.Forms.OpenFileDialog
    $dialog.Filter = "All files (*.*)|*.*"
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $txtInput.Text = $dialog.FileName
    }
})

$btnRun.Add_Click({
    $inputFile = $txtInput.Text.Trim()
    $lang = if ([string]::IsNullOrWhiteSpace($txtLang.Text)) { "nl" } else { $txtLang.Text.Trim() }
    $timestamp = $txtTimestamp.Text.Trim()
    $outputDir = "C:\Users\WhisperX\Desktop\output"
    $scriptDir = "C:\Users\WhisperX\Documents\whisperX"

    if (-not (Test-Path $inputFile)) {
        [System.Windows.Forms.MessageBox]::Show("Please select a valid input file.", "Error", 0, 16)
        return
    }

    # Build WhisperX argument list
    $args = @(
        "`"$inputFile`"",
        "--output_dir", "`"$outputDir`"",
        "--model", "large",
        "--device", "cuda",
        "--compute_type", "float16",
        "--diarize",
        "--diarize_offline",
        "--diarize_config", "models/pyannote_diarization_config.yaml",
        "--model_cache_only", "True",
        "--model_dir", "models",
        "--language", $lang,
        "--output_format", "srt"
    )

    $txtOutput.Text = "Running WhisperX..."
    try {
        Start-Process -FilePath "whisperx" -ArgumentList $args -NoNewWindow -Wait
        $txtOutput.AppendText("`r`nWhisperX finished successfully.`r`n")

        # Always run add_timestamp.py — default to 00:00:00 if none provided
        if ([string]::IsNullOrWhiteSpace($timestamp)) {
            $timestamp = "00:00:00"
            $txtOutput.AppendText("No timestamp entered - defaulting to 00:00:00.`r`n")
        }

        $fileName = [System.IO.Path]::GetFileNameWithoutExtension($inputFile)
        $srtFile = Join-Path $outputDir ($fileName + ".srt")

        if (Test-Path $srtFile) {
            $txtOutput.AppendText("Adding timestamp $timestamp to $srtFile...`r`n")

            $args2 = @(
                "`"$scriptDir\whisperx\add_timestamp.py`"",
                "`"$srtFile`"",
                "--timestamp", "`"$timestamp`""
            )

            Start-Process -FilePath "python" -ArgumentList $args2 -NoNewWindow -Wait
            $txtOutput.AppendText("Timestamp added successfully.`r`n")
        } else {
            $txtOutput.AppendText("Could not find the .srt file after WhisperX finished.`r`n")
        }

    } catch {
        $txtOutput.AppendText("Error: $($_.Exception.Message)`r`n")
    }
})

# === SHOW GUI ===
$form.Topmost = $true
$form.ShowDialog()
