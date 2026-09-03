# Generates a real speech WAV for the Groq STT diagnostic using the
# Windows built-in synthesizer (no external dependencies).
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile("d:\interviAI\backend\diag_sample.wav")
$synth.Speak("Hello, this is a test of the speech transcription service for the interview platform.")
$synth.Dispose()
Write-Host "diag_sample.wav created"
