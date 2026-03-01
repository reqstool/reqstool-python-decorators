from reqstool_python_decorators.decorators.decorators import SVCs


@SVCs("SVC_999")
def test_first_svc_test():
    # Test "test" for SVC decorator
    pass


@SVCs("SVC_999", "SVC_123")
def test_second_svc_test():
    # Test "test" for SVC decorator
    pass
