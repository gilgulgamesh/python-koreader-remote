#!/usr/bin/env python3
# kobo-keys.py — low-latency arrow → Koreader HTTP with hold-repeat
# Requires: pip install pynput requests

import time
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
from pynput import keyboard
import pygetwindow as gw

TERMINAL_KEYWORDS = ["Terminal", "terminal", "iTerm2", "iTerm", "Windows PowerShell", "cmd", "Command Prompt", "pwsh"]

def terminal_focused():
    try:
        win = gw.getActiveWindow()
        if not win:
            return False
        title = (win.title or "")
        for k in TERMINAL_KEYWORDS:
            if k.lower() in title.lower():
                return True
    except Exception:
        return False
    return False

# CONFIG
IP_PORT = "192.168.1.109:8080"   # set your Kobo IP:PORT
BASE = f"http://{IP_PORT}/koreader/event"
TIMEOUT = 0.6                   # requests timeout in seconds
DEBOUNCE = 0.04                 # minimum seconds between sends per direction
REPEAT_HZ = 3                  # sends per second while holding (e.g., 18 -> ~56ms)
MAX_WORKERS = 4                 # thread pool size

# INTERNAL
_session = requests.Session()
_executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
_last_sent = {"left": 0.0, "right": 0.0, "space": 0.0}
_hold_state = {"left": False, "right": False, "space": False}
_hold_timers = {"left": None, "right": None, "space": None} 
_interval = 1.0 / REPEAT_HZ

def _send_http(path):
    try:
        _session.get(f"{BASE}/{path}", timeout=TIMEOUT)
    except requests.RequestException:
        pass

def send_nonblocking(path):
    _executor.submit(_send_http, path)

def _maybe_send(direction, path):
    now = time.time()
    if now - _last_sent[direction] >= DEBOUNCE:
        _last_sent[direction] = now
        send_nonblocking(path)

def _hold_loop(direction, path):
    # Called in a background thread to repeatedly send while holding
    while _hold_state[direction]:
        _maybe_send(direction, path)
        time.sleep(_interval)

def on_press(key):
    try:
        if key == keyboard.Key.left:
            if _hold_state["left"]:
                return
            _hold_state["left"] = True
            _maybe_send("left", "GotoViewRel/-1")
            t = threading.Thread(target=_hold_loop, args=("left", "GotoViewRel/-1"), daemon=True)
            _hold_timers["left"] = t
            t.start()
        elif key == keyboard.Key.right:
            if _hold_state["right"]:
                return
            _hold_state["right"] = True
            _maybe_send("right", "GotoViewRel/1")
            t = threading.Thread(target=_hold_loop, args=("right", "GotoViewRel/1"), daemon=True)
            _hold_timers["right"] = t
            t.start()
        elif key == keyboard.Key.space:
            if not terminal_focused():
                return
            if _hold_state["space"]:
                return
            _hold_state["space"] = True
            _maybe_send("space", "GotoViewRel/1")
            t = threading.Thread(target=_hold_loop, args=("space", "GotoViewRel/1"), daemon=True)
            _hold_timers["space"] = t
            t.start()

        elif key == keyboard.Key.esc:
            # stop listener
            return False
    except AttributeError:
        pass

def on_release(key):
    try:
        if key == keyboard.Key.left:
            _hold_state["left"] = False
            _hold_timers["left"] = None
        elif key == keyboard.Key.right:
            _hold_state["right"] = False
            _hold_timers["right"] = None
            
        elif key == keyboard.Key.space:
            _hold_state["space"] = False
            _hold_timers["space"] = None
    except AttributeError:
        pass

def main():
    print("Listening for space while focussed, or left/right arrows anywhere. Hold to repeat. Esc to quit.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()

