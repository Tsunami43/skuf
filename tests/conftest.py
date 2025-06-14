from unittest import TestCase

from skuf import DIContainer


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
        # Clear the internal registry before each test
        DIContainer.clear()
