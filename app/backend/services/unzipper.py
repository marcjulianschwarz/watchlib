import argparse
import json
import zipfile
from pathlib import Path

from default_service import Service


class Unzipper(Service):
    def __init__(self, config, service_path):
        super().__init__("unzipper", config, service_path)
        self.user = config["user"]
        self.zip_path = Path(config["zip_path"])

    def done(self):
        open(self.service_path / ".done", "w").close()

    def run(self):
        zip_ref = zipfile.ZipFile(self.zip_path, "r")
        zip_ref.extractall("user_dir/" + self.user)
        zip_ref.close()
        self.done()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("service_config", type=str)
    arg_parser.add_argument("service_path", type=str)
    args = arg_parser.parse_args()
    SERVICE_CONFIG = json.loads(args.service_config)
    Unzipper(SERVICE_CONFIG, args.service_path).run()
