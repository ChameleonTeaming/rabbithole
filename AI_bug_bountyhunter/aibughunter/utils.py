import sys
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

class Logger:
    @staticmethod
    def info(msg):
        print(f"{Fore.CYAN}[INFO] {msg}{Style.RESET_ALL}")

    @staticmethod
    def success(msg):
        print(f"{Fore.GREEN}[SUCCESS] {msg}{Style.RESET_ALL}")

    @staticmethod
    def warning(msg):
        print(f"{Fore.YELLOW}[WARNING] {msg}{Style.RESET_ALL}")

    @staticmethod
    def error(msg):
        print(f"{Fore.RED}[ERROR] {msg}{Style.RESET_ALL}")

    @staticmethod
    def header(msg):
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}=== {msg} ==={Style.RESET_ALL}\n")
