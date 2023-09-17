from pathlib import Path
from datetime import datetime
from termcolor import colored
import time

class logger:

    def __init__(self):
        now = datetime.now()
        self.session_date = now.strftime('%Y%m%d%H%M%S')
        self.session_file = 'log_' + str(self.session_date)
        root = Path('.')
        self.logfile_path = root / 'logs' / self.session_file
        with self.logfile_path.open('a') as f:
            f.write(f'-----------------------------------------------\n')
            f.write(f'### Galaxy Log File for {now.strftime("%d/%m/%Y %H:%M:%S")} ###\n')
            f.write(f'-----------------------------------------------\n\n')
        self.welcome_message()
        self.print_general('Log file created for session.')

    def log_general(self, message):
        now = datetime.now()
        current_time = now.strftime('%Y/%m/%d_%H:%M:%S')
        with self.logfile_path.open('a') as f:
            f.write(current_time + ' ' + message + '\n')

    def print_general(self, message):
        self.log_general('[*] ' + message)
        print(colored('[*]', 'blue'), end=' ')
        print(colored(message, 'white'))

    def print_success(self, message):
        self.log_general('[+] ' + message)
        print(colored('[+]', 'green'), end=' ')
        print(colored(message, 'green'))

    def print_warning(self, message):
        self.log_general('[~] ' + message)
        print(colored('[~]', 'yellow'), end=' ')
        print(colored(message, 'yellow'))

    def print_error(self, message):
        self.log_general('[x] ' + message)
        print(colored('[x]', 'red'), end=' ')
        print(colored(message, 'red'))

    def welcome_message(self):
        text = open('artwork/welcome.txt').read()
        print(colored(text, 'blue', 'on_white'))
        quote = open('artwork/quote.txt').read()
        print(colored(quote, 'blue', 'on_white'))
        print()
        time.sleep(2)
        return