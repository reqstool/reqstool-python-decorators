from reqstool_python_decorators.decorators.decorators import Requirements


@Requirements("REQ_001", "REQ_222")
class RequirementsClass:
    pass


@Requirements("REQ_333")
def requirements_function() -> None:
    # Test function for Requirements decorator
    pass


@Requirements("REQ_444")
async def asyncrequirements_function() -> None:
    # Test async function for Requirements decorator
    pass
