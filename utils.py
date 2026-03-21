"""
utils.py — Shared helpers for logging, formatting, and terminal output.
"""

import logging
import sys
from datetime import datetime


# ─── Logging Setup ────────────────────────────────────────────
def setup_logger(name: str = "stock_predictor", level: int = logging.INFO) -> logging.Logger:
    """Create a formatted logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s │ %(levelname)-8s │ %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = setup_logger()


# ─── ANSI Color Helpers ──────────────────────────────────────
class Colors:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Colors.RESET}"


def green(text: str) -> str:
    return colorize(text, Colors.GREEN)


def red(text: str) -> str:
    return colorize(text, Colors.RED)


def yellow(text: str) -> str:
    return colorize(text, Colors.YELLOW)


def cyan(text: str) -> str:
    return colorize(text, Colors.CYAN)


def bold(text: str) -> str:
    return colorize(text, Colors.BOLD)


def dim(text: str) -> str:
    return colorize(text, Colors.DIM)


# ─── Formatting Helpers ──────────────────────────────────────
def format_price(price: float, decimals: int = 2) -> str:
    return f"${price:,.{decimals}f}"


def format_percent(value: float, decimals: int = 2) -> str:
    sign = "+" if value >= 0 else ""
    color = Colors.GREEN if value >= 0 else Colors.RED
    return colorize(f"{sign}{value:.{decimals}f}%", color)


def format_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


# ─── Box Drawing ──────────────────────────────────────────────
def print_header(title: str) -> None:
    width = 60
    print()
    print(cyan("═" * width))
    print(cyan("║") + bold(f" {title}".center(width - 2)) + cyan("║"))
    print(cyan("═" * width))


def print_section(title: str) -> None:
    print()
    print(yellow(f"── {title} " + "─" * (45 - len(title))))


def print_kv(key: str, value: str, indent: int = 2) -> None:
    print(f"{' ' * indent}{dim(key + ':')} {value}")


def print_divider() -> None:
    print(dim("─" * 60))
