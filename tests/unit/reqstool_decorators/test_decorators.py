# Copyright © LFV

from reqstool_python_decorators.decorators.decorators import Requirements, SVCs

# NOTE: these tests apply Requirements/SVCs via direct call (`Requirements(...)(func)`)
# rather than `@Requirements(...)` decorator syntax. Decorator syntax would make the
# nested function/class defs below show up as real, AST-discoverable annotations when
# this repo self-applies its own processor (see scripts/generate_annotations.py) --
# polluting the project's own requirement/SVC traceability data with these fake IDs.


@SVCs("SVC_DECORATORS_001")
def test_requirements_sets_attribute():
    def func():
        pass

    func = Requirements("REQ_001")(func)

    assert func.requirements == ("REQ_001",)


@SVCs("SVC_DECORATORS_001")
def test_requirements_multiple_ids():
    def func():
        pass

    func = Requirements("A", "B")(func)

    assert func.requirements == ("A", "B")


@SVCs("SVC_DECORATORS_001")
def test_requirements_preserves_function_name():
    def my_function():
        pass

    my_function = Requirements("REQ_001")(my_function)

    assert my_function.__name__ == "my_function"


@SVCs("SVC_DECORATORS_001")
def test_svcs_sets_attribute():
    def func():
        pass

    func = SVCs("SVC_001")(func)

    assert func.svc_ids == ("SVC_001",)


@SVCs("SVC_DECORATORS_001")
def test_svcs_multiple_ids():
    def func():
        pass

    func = SVCs("A", "B")(func)

    assert func.svc_ids == ("A", "B")


@SVCs("SVC_DECORATORS_001")
def test_svcs_preserves_function_name():
    def my_function():
        pass

    my_function = SVCs("SVC_001")(my_function)

    assert my_function.__name__ == "my_function"


@SVCs("SVC_DECORATORS_001")
def test_requirements_on_class():
    class MyClass:
        pass

    MyClass = Requirements("REQ_001")(MyClass)

    assert MyClass.requirements == ("REQ_001",)


@SVCs("SVC_DECORATORS_001")
def test_requirements_on_async_function():
    async def my_async_function():
        pass

    my_async_function = Requirements("REQ_001")(my_async_function)

    assert my_async_function.requirements == ("REQ_001",)


@SVCs("SVC_DECORATORS_001")
def test_svcs_on_async_function():
    async def my_async_function():
        pass

    my_async_function = SVCs("SVC_001")(my_async_function)

    assert my_async_function.svc_ids == ("SVC_001",)


@SVCs("SVC_DECORATORS_001")
def test_svcs_on_class():
    class MyClass:
        pass

    MyClass = SVCs("SVC_001")(MyClass)

    assert MyClass.svc_ids == ("SVC_001",)
