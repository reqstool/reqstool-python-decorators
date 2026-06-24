# Copyright © LFV

from collections.abc import Callable


def Requirements[T: Callable](*requirements: str) -> Callable[[T], T]:
    def decorator(func: T) -> T:
        func.requirements = requirements  # type: ignore[attr-defined]
        return func

    return decorator


# Tagged here rather than on Requirements: by the time SVCs is defined, Requirements
# is already bound in module scope, so it can reference it as a decorator. Requirements
# can't self-tag this way (its own name isn't bound yet at its own def statement), but
# both factories jointly implement DECORATORS_001 -- this tag location is just where
# that fact gets recorded.
@Requirements("DECORATORS_001")
def SVCs[T: Callable](*svc_ids: str) -> Callable[[T], T]:
    def decorator(func: T) -> T:
        func.svc_ids = svc_ids  # type: ignore[attr-defined]
        return func

    return decorator
