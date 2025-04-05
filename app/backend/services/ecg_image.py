import argparse
import json
from pathlib import Path

from default_service import Service
from watchml import ECGReader


class ECGImage(Service):
    def __init__(self, config, service_path):
        super().__init__("ecg_image", config, service_path)
        self.user = config["user"]
        self.ecg_path = config["ecg_path"]

    def done(self):
        open(self.service_path / ".done", "w").close()

    def run(self):
        ECGReader.read_ecg_from_file(self.ecg_path).generate_plot(
            self.ecg_path.replace(".csv", ".png")
        )
        self.done()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("service_config", type=str)
    arg_parser.add_argument("service_path", type=str)
    args = arg_parser.parse_args()
    SERVICE_CONFIG = json.loads(args.service_config)
    ECGImage(SERVICE_CONFIG, args.service_path).run()
