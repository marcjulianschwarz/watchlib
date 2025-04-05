import argparse
import json
from pathlib import Path

from default_service import Service


class TestService(Service):
    def __init__(self, config):
        super().__init__("test_service", config)
        self.service_path = Path(config["service_path"])

    def done(self):
        open(self.service_path / ".done", "w").close()

    def run(self):
        print("Test service is running")
        self.done()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("service_config", type=str)
    args = arg_parser.parse_args()
    SERVICE_CONFIG = json.loads(args.service_config)
    TestService(SERVICE_CONFIG).run()
