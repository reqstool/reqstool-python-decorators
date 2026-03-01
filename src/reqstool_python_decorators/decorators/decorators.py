# Copyright © LFV

from collections.abc import Callable


def Requirements[T: Callable](*requirements: str) -> Callable[[T], T]:
    def decorator(func: T) -> T:
        func.requirements = requirements  # type: ignore[attr-defined]
        return func

    return decorator


def SVCs[T: Callable](*svc_ids: str) -> Callable[[T], T]:
    def decorator(func: T) -> T:
        func.svc_ids = svc_ids  # type: ignore[attr-defined]
        return func

    return decorator
