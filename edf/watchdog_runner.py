import subprocess
import time
import os
from datetime import datetime

bot_script = "adumb_bot.py"
log_file = "adumb_watchdog.log"

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

def run_bot():
    log("Starting Adumb bot...")
    return subprocess.Popen(["python3", bot_script])

if __name__ == "__main__":
    process = run_bot()

    while True:
        try:
            # Wait for the bot to exit (blocking)
            code = process.wait()
            log(f"Bot exited with code {code}")

            # If it exited unexpectedly, restart after delay
            if code != 0:
                log("Bot crashed. Restarting in a few seconds...")
                time.sleep(3)
                process = run_bot()
            else:
                log("Bot exited cleanly. Watchdog will stop.")
                break

        except KeyboardInterrupt:
            log("Watchdog interrupted. Shutting down.")
            process.terminate()
            break
