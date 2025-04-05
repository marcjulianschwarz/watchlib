import json
import os
import shutil
import time as t
from pathlib import Path


class ServiceProvider:
    def __init__(self):
        self.SERVICE_REQUEST_DIR = Path("./service_dir")
        self.SERVICES_DIR = Path("./services")

    def is_service_done(self, service_request):
        return os.path.exists(self.SERVICE_REQUEST_DIR / service_request / ".done")

    def delete_service_request(self, service_request):
        shutil.rmtree(self.SERVICE_REQUEST_DIR / service_request)

    def is_service_running(self, service_request):
        return os.path.exists(self.SERVICE_REQUEST_DIR / service_request / ".running")

    def is_service_runnable(self, service_request):
        return os.path.exists(
            self.SERVICE_REQUEST_DIR / service_request / "service.json"
        )

    def start_service(self, service_request):
        config = json.load(
            open(self.SERVICE_REQUEST_DIR / service_request / "service.json", "r")
        )
        service_id = config["service_id"]
        service_config = config["service_config"]
        service_path = config["service_path"]

        print(f"Starting service {service_id}")
        os.system(
            f"python3 {self.SERVICES_DIR / (service_id + '.py')} '{json.dumps(service_config)}'  '{service_path}'"
        )
        open(self.SERVICE_REQUEST_DIR / service_request / ".running", "w").close()

    def run(self):
        while True:
            service_requests = os.listdir(self.SERVICE_REQUEST_DIR)
            service_requests = [sr for sr in service_requests if not sr.startswith(".")]

            if len(service_requests) == 0:
                t.sleep(0.5)
                continue

            for service_request in service_requests:
                if self.is_service_done(service_request):
                    self.delete_service_request(service_request)
                    print(f"Service {service_request} is done")
                    continue

                if self.is_service_running(service_request):
                    continue

                if self.is_service_runnable(service_request):
                    self.start_service(service_request)


if __name__ == "__main__":
    sp = ServiceProvider()
    sp.run()
