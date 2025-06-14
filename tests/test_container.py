from tests.conftest import *


class TestDIContainer(TestSkuf):
    def test_register_instance_returns_same_instance(self):
        logger = Logger()
        DIContainer.register(Logger, instance=logger)
        self.assertIs(DIContainer.resolve(Logger), logger)

    def test_register_class_creates_new_instances(self):
        DIContainer.register(Logger)
        instance1 = DIContainer.resolve(Logger)
        instance2 = DIContainer.resolve(Logger)
        self.assertIsInstance(instance1, Logger)
        self.assertIsInstance(instance2, Logger)
        self.assertIsNot(instance1, instance2)

    def test_register_factory_creates_new_instances(self):
        DIContainer.register(Logger, factory=lambda: Logger())
        instance1 = DIContainer.resolve(Logger)
        instance2 = DIContainer.resolve(Logger)
        self.assertIsNot(instance1, instance2)

    def test_resolve_unregistered_raises_value_error(self):
        with self.assertRaises(ValueError):
            DIContainer.resolve(Dummy)

    def test_factory_returns_wrong_type_raises_type_error(self):
        DIContainer.register(Logger, factory=lambda: Dummy())
        with self.assertRaises(TypeError):
            DIContainer.resolve(Logger)
