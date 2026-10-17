"""Program 62: Print Colored Text to the Terminal

Demonstrates printing colored text using ANSI escape codes.

Reference: https://www.programiz.com/python-programming/examples/colored-terminal
"""


# ANSI escape code color constants
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    # Bold
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


def colored(text: str, color: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{color}{text}{Colors.RESET}"


def main() -> None:
    """Display colored text examples."""
    print(colored("This is RED text", Colors.RED))
    print(colored("This is GREEN text", Colors.GREEN))
    print(colored("This is BLUE text", Colors.BLUE))
    print(colored("This is YELLOW text", Colors.YELLOW))
    print(colored("This is MAGENTA text", Colors.MAGENTA))
    print(colored("This is CYAN text", Colors.CYAN))
    print(colored("This is BOLD text", Colors.BOLD))
    print(colored("This is UNDERLINED text", Colors.UNDERLINE))
    print(colored("This has a RED background", Colors.BG_RED))
    print(colored("This has a GREEN background", Colors.BG_GREEN))

    # Combined styles
    print(f"{Colors.BOLD}{Colors.RED}Bold and Red{Colors.RESET}")
    print(f"{Colors.UNDERLINE}{Colors.BLUE}Underlined and Blue{Colors.RESET}")


if __name__ == "__main__":
    main()
