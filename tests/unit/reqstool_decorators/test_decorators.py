# Copyright © LFV

from reqstool_python_decorators.decorators.decorators import Requirements, SVCs


def test_requirements_sets_attribute():
    @Requirements("REQ_001")
    def func():
        pass

    assert func.requirements == ("REQ_001",)


def test_requirements_multiple_ids():
    @Requirements("A", "B")
    def func():
        pass

    assert func.requirements == ("A", "B")


def test_requirements_preserves_function_name():
    @Requirements("REQ_001")
    def my_function():
        pass

    assert my_function.__name__ == "my_function"


def test_svcs_sets_attribute():
    @SVCs("SVC_001")
    def func():
        pass

    assert func.svc_ids == ("SVC_001",)


def test_svcs_multiple_ids():
    @SVCs("A", "B")
    def func():
        pass

    assert func.svc_ids == ("A", "B")


def test_svcs_preserves_function_name():
    @SVCs("SVC_001")
    def my_function():
        pass

    assert my_function.__name__ == "my_function"


def test_requirements_on_class():
    @Requirements("REQ_001")
    class MyClass:
        pass

    assert MyClass.requirements == ("REQ_001",)
