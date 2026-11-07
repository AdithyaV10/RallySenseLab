param(
    [Parameter(Mandatory=$true)][string]$LanAddress,
    [Parameter(Mandatory=$true)][string]$Certificate,
    [Parameter(Mandatory=$true)][string]$Key,
    [switch]$Start
)
$ErrorActionPreference = 'Stop'
$parsed = $null
if (-not [Net.IPAddress]::TryParse($LanAddress, [ref]$parsed) -or $parsed.AddressFamily -ne [Net.Sockets.AddressFamily]::InterNetwork) { throw 'Use an explicit private IPv4 address.' }
$octets = $parsed.GetAddressBytes()
$privateAddress = $octets[0] -eq 10 -or ($octets[0] -eq 172 -and $octets[1] -ge 16 -and $octets[1] -le 31) -or ($octets[0] -eq 192 -and $octets[1] -eq 168)
if (-not $privateAddress) { throw 'Only RFC1918 LAN addresses are accepted; wildcard/public bindings are refused.' }
if (-not (Get-NetIPAddress -AddressFamily IPv4 | Where-Object IPAddress -eq $LanAddress)) { throw 'Address is not assigned to a local network adapter.' }
$certificatePath = (Resolve-Path -LiteralPath $Certificate).Path
$keyPath = (Resolve-Path -LiteralPath $Key).Path
if (-not $env:SITE_ACCESS_PASSWORD -or $env:SITE_ACCESS_PASSWORD.Length -lt 20) { throw 'Set SITE_ACCESS_PASSWORD to a unique password of at least 20 characters. It is never printed.' }
if (-not $env:LOCAL_TOKEN) { throw 'Set LOCAL_TOKEN to match the running loopback API. Do not expose this token to the phone.' }
$workspacePath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$webPath = Join-Path $workspacePath 'apps/web'
$cliPath = Join-Path $webPath 'node_modules/next/dist/bin/next'
if (-not (Test-Path -LiteralPath $cliPath -PathType Leaf)) { throw 'Install locked web dependencies first: npm.cmd ci --prefix apps/web' }
Write-Output "Prepared private HTTPS at https://${LanAddress}:3443. Browser username: lab. Certificate must include this IP and be trusted by the phone. No CA or firewall changes are made."
if (-not $Start) { Write-Output 'Preparation only. Add -Start when you explicitly want to start the LAN listener.'; return }
$previous = @{}
$settings = @{ WEB_ALLOWED_HOSTS="127.0.0.1,localhost,$LanAddress"; WEB_ALLOWED_ORIGINS="https://${LanAddress}:3443"; API_INTERNAL_URL='http://127.0.0.1:8000'; RALLYSENSE_DEV_ORIGIN=$LanAddress }
try {
    foreach ($name in $settings.Keys) { $previous[$name] = [Environment]::GetEnvironmentVariable($name,'Process'); [Environment]::SetEnvironmentVariable($name,$settings[$name],'Process') }
    Push-Location -LiteralPath $webPath
    try { & node $cliPath dev --hostname $LanAddress --port 3443 --experimental-https --experimental-https-key $keyPath --experimental-https-cert $certificatePath }
    finally { Pop-Location }
} finally { foreach ($name in $settings.Keys) { [Environment]::SetEnvironmentVariable($name,$previous[$name],'Process') } }
