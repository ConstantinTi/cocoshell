# cocoshell

## Purpose
The cocoshell is really a project for to learn about reverse shells and the evasion of any kind of security measures. In my daily life as a penetration tester I permanently get faced with the challeng to evade different security tools. I would rather have a more basic shell, that works in almost any project than being caught by the customers SOCs.

## Concept
For now, the shell is really, really basic. You have a flask API with just one endpoint, that provides the command, the victim should run and can accept the ouput of that command. Right now, the shell does not get caught by any security solutions.

## Install
You just need `python3` and `pip` installed.
```shell
git clone https://github.com/ConstantinTi/cocoshell.git
cd cocoshell
pip3 install -r requirements.txt
python3 cocoshell.py
```

## ToDo / Known issues
* Commands that fail don't show the error output of the command
* Communcation is completely based on http for now and not encrypted at all
* There is no possibility to configure anything with arguments
* You cannot have multiple agents running (which might not be that much of a problem)
* You cannot see the current working directory of the agent
* The powershell code is not obfuscated and there is no generator for that either
* The endpoint of the API is hardcoded to `test`
* The logging is quite ugly
* The shell will hang if you execute a command that creates an interactive3 shell session
* Constrained language mode might be interesting to bypass
* ExecutionPolicy might be interesting to bypass