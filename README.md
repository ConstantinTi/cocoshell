# cocoshell

## Purpose
The cocoshell is really a project for to learn about reverse shells and the evasion of any kind of security measures. In my daily life as a penetration tester I permanently get faced with the challenge to evade different security tools. I would rather have a more basic shell, that works in almost any project than being caught by the customers SOCs.

## Concept
For now, the shell is really, really basic. You have a flask API with just one endpoint, that provides the command, the victim should run and can accept the ouput of that command. Right now, the shell does not get caught by any security solutions.

## Install
You just need `python3` and `pip` installed.
```shell
sudo apt install python3 python3-pip
git clone https://github.com/ConstantinTi/cocoshell.git
cd cocoshell
pip3 install -r requirements.txt
python3 cocoshell.py
```