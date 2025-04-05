from pathlib import Path


class Service:
    def __init__(self, name, config, service_path):
        self.name = name
        self.config = config
        self.service_path = Path(service_path)

    def run(self):
        pass
