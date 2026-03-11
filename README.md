# python-koreader-remote
Control koreader remotely from any device running python, within the local network

## Features

It simply listens for space when the terminal is in focus, and arrow keys regardless.

## Installation

1. Requires python (install to PATH is always simplest, but find instructions for your device)

2. Dependencies installed via pip (may vary as per your instalatlattion or OS)
> pip install pynput requests pygetwindow

3. Download the KoRemote.py file from github (click on it, then raw) noting the path to the file (you can copy the path to it too)


## Configutation

1. Enable Koreader HTTP Inspector, under Tools//More tools

2. Enable wifi under Settings//Network, then press **Network Information** To view the eReader's IP address

3. Edit the KoRemote.py file to change the predefined IP address (mine) to yours. It should only differ in the last few numbers.

To run the app simply run
> python \<path-to-file\>/KoRemote.py

(Save this command for next time)

## Disclaimer
This was vibe-coded with gpt-5 mini through [Duck.ai](https://duck.ai). I do recommend this approach if you want to change keybinds, behaviours, or troubleshoot python installation
