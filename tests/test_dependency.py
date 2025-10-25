from skuf import Dependency

from tests.conftest import *


class TestDependency(TestSkuf):
    def test_dependency_returns_instance(self):
        Dependency.register(Logger)
        self.assertIsInstance(Dependency.resolve(Logger), Logger)

    def test_dependency_returns_same_as_container(self):
        logger = Logger()
        Dependency.register(Logger, instance=logger)
        self.assertIs(Dependency.resolve(Logger), logger)

    def test_dependency_raises_value_error(self):
        with self.assertRaises(ValueError):
            Dependency.resolve(Dummy)

    def test_dependency_raises_type_error(self):
        Dependency.register(Logger, factory=lambda: Dummy())
        with self.assertRaises(TypeError):
            Dependency.resolve(Logger)

    def test_dependency_on_param_func(self):
        Dependency.register(Logger)

        def func(logger=Dependency(Logger)):
            return logger.log("Working")

        self.assertEqual(func(), "Working")
