class Logger:
    
    def __init__(self, print_to_console=True, log_level=0, log_to_file=False):
        self.print_to_console = print_to_console
        self.log_level = log_level
        self.log_to_file = log_to_file
        pass

    def log(self, message):
        print(message)

    