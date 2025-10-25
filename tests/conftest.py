import os
from typing import List
from unittest import TestCase

from skuf import Dependency, BaseSettings


class Logger:
    def log(self, msg: str):
        return msg


class Service:
    def __init__(self, logger: Logger):
        self.logger = logger

    def work(self):
        return self.logger.log("Working")


class Dummy:
    pass


class TestSkuf(TestCase):
    def setUp(self):
        Dependency.clear()


class TestSetUpBaseSettings(TestCase):
    def setUp(self) -> None:
        os.environ["TOKEN"] = "abc123"
        os.environ["RETRIES"] = "3"
        os.environ["DEBUG"] = "true"
        os.environ["TIMEOUT"] = "2.5"
        os.environ["SERVERS"] = "server1|server2|server3"
        os.environ["PORTS"] = "8000|8001|8002"

    def tearDown(self) -> None:
        for var in ["TOKEN", "RETRIES", "DEBUG", "TIMEOUT", "SERVERS", "PORTS"]:
            os.environ.pop(var, None)


class SettingsExample(BaseSettings):
    token: str
    retries: int
    debug: bool
    timeout: float
    servers: List[str]
    ports: List[int]
