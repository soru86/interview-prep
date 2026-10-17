"""Program 95: Create a Countdown Timer

Demonstrates creating a simple countdown timer using the time module.

Reference: https://www.programiz.com/python-programming/examples/countdown-timer
"""

import time
import sys


def countdown(seconds: int) -> None:
    """Run a countdown timer for the specified number of seconds."""
    print(f"Starting {seconds}-second countdown...")
    
    while seconds > 0:
        # Calculate minutes and seconds
        mins, secs = divmod(seconds, 60)
        timer = f"{mins:02d}:{secs:02d}"
        
        # Print using carriage return to overwrite the line
        print(timer, end="\r")
        
        # Wait 1 second
        time.sleep(1)
        seconds -= 1
        
    print("00:00")
    print("Time's up!")


def main() -> None:
    """Run a sample countdown timer."""
    try:
        # We'll use a short 5-second timer for demonstration
        # to avoid making the user wait too long
        countdown(5)
    except KeyboardInterrupt:
        print("\nCountdown interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
