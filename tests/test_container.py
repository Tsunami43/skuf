from skuf import Dependency
from tests.conftest import *


class TestDependencyContainer(TestSkuf):
    def test_register_instance_returns_same_instance(self):
        logger = Logger()
        Dependency.register(Logger, instance=logger)
        self.assertIs(Dependency.resolve(Logger), logger)

    def test_register_class_creates_new_instances(self):
        Dependency.register(Logger)
        instance1 = Dependency.resolve(Logger)
        instance2 = Dependency.resolve(Logger)
        self.assertIsInstance(instance1, Logger)
        self.assertIsInstance(instance2, Logger)
        self.assertIsNot(instance1, instance2)

    def test_register_factory_creates_new_instances(self):
        Dependency.register(Logger, factory=lambda: Logger())
        instance1 = Dependency.resolve(Logger)
        instance2 = Dependency.resolve(Logger)
        self.assertIsNot(instance1, instance2)

    def test_resolve_unregistered_raises_value_error(self):
        with self.assertRaises(ValueError):
            Dependency.resolve(Dummy)

    def test_factory_returns_wrong_type_raises_type_error(self):
        Dependency.register(Logger, factory=lambda: Dummy())
        with self.assertRaises(TypeError):
            Dependency.resolve(Logger)
