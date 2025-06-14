from skuf import Dependency

from tests.conftest import *


class TestDependency(TestSkuf):
    def test_dependency_returns_instance(self):
        DIContainer.register(Logger)
        self.assertIsInstance(Dependency(Logger), Logger)

    def test_dependency_returns_same_as_container(self):
        logger = Logger()
        DIContainer.register(Logger, instance=logger)
        self.assertIs(Dependency(Logger), logger)

    def test_dependency_raises_value_error(self):
        with self.assertRaises(ValueError):
            Dependency(Dummy)

    def test_dependency_raises_type_error(self):
        DIContainer.register(Logger, factory=lambda: Dummy())
        with self.assertRaises(TypeError):
            Dependency(Logger)

    def test_dependency_on_param_func(self):
        DIContainer.register(Logger)

        def func(logger=Dependency(Logger)):
            return logger.log("Working")

        self.assertEqual(func(), "Working")
