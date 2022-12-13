$ProgressPreference = 'SilentlyContinue'
#while ($true)
#{
    $cmd = ConvertFrom-Json (Invoke-WebRequest 'http://localhost:5000/test')
    if (!$cmd.code) 
    { 
        if ($cmd.cmd -eq "exit-agent") { break }
        $result = Invoke-Expression ($cmd.cmd)
        write-host $result
        if( -not $? ) { $result = $Error[0].Exception.Message }
        $post = @{"id"=$cmd.id;"result"=$result;}
        #write-host (ConvertTo-Json $result)
        #Invoke-WebRequest -Uri http://localhost:5000/test -Method POST -Body (ConvertTo-Json $post) -ContentType 'application/json; charset=utf-8'
        #Invoke-RestMethod -Uri http://localhost:5000/test -Method POST -Body (ConvertTo-Json $post) -ContentType 'application/json; charset=utf-8'
    }
    else
    { }
#}