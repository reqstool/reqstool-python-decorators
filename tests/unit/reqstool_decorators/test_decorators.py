# Copyright © LFV

import pytest
from reqstool_python_decorators.decorators.decorators import Requirements, SVCs

# NOTE: these tests apply Requirements/SVCs via direct call (`Requirements(...)(func)`)
# rather than `@Requirements(...)` decorator syntax. Decorator syntax would make the
# nested function/class defs below show up as real, AST-discoverable annotations when
# this repo self-applies its own processor (see scripts/generate_annotations.py) --
# polluting the project's own requirement/SVC traceability data with these fake IDs.


def _function():
    pass


async def _async_function():
    pass


class _Class:
    pass


@SVCs("SVC_DECORATORS_001")
@pytest.mark.parametrize(
    "decorator_factory,attr_name,target",
    [
        (Requirements, "requirements", _function),
        (Requirements, "requirements", _async_function),
        (Requirements, "requirements", _Class),
        (SVCs, "svc_ids", _function),
        (SVCs, "svc_ids", _async_function),
        (SVCs, "svc_ids", _Class),
    ],
    ids=[
        "requirements-on-function",
        "requirements-on-async-function",
        "requirements-on-class",
        "svcs-on-function",
        "svcs-on-async-function",
        "svcs-on-class",
    ],
)
def test_sets_attribute_on_target(decorator_factory, attr_name, target):
    decorated = decorator_factory("REQ_001")(target)

    assert getattr(decorated, attr_name) == ("REQ_001",)


@SVCs("SVC_DECORATORS_001")
@pytest.mark.parametrize(
    "decorator_factory,attr_name",
    [(Requirements, "requirements"), (SVCs, "svc_ids")],
    ids=["requirements", "svcs"],
)
def test_multiple_ids(decorator_factory, attr_name):
    target = decorator_factory("A", "B")(_function)

    assert getattr(target, attr_name) == ("A", "B")


@SVCs("SVC_DECORATORS_001")
@pytest.mark.parametrize("decorator_factory", [Requirements, SVCs], ids=["requirements", "svcs"])
def test_preserves_function_name(decorator_factory):
    target = decorator_factory("REQ_001")(_function)

    assert target.__name__ == "_function"
