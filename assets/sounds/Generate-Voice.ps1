[CmdletBinding()]
param (
    [Parameter()]
    [String] $Text,
    [Parameter()]
    [String] $Voice = "en-US-ChristopherNeural"
)

if ($null -eq $Env:AZURE_SPX_KEY) {
    Write-Error "Please set the environment variable AZURE_SPX_KEY to your Azure Speech Service key."
    exit 1
}
if ($null -eq $Env:AZURE_SPX_REGION) {
    Write-Error "Please set the environment variable AZURE_SPX_REGION to your Azure Speech Service region."
    exit 1
}


spx synthesize --text "$Text" --voice $Voice --audio output "o.wav" --key $Env:AZURE_SPX_KEY --region $Env:AZURE_SPX_REGION
ffmpeg -i "o.wav" -af silenceremove=start_periods=1:start_threshold=-60dB:detection=peak,areverse,silenceremove=start_periods=1:start_threshold=-60dB:detection=peak,areverse "t.wav"
ffmpeg -i "t.wav" -ac 1 -ar 8000 -acodec pcm_u8 -f u8 "text.raw"
