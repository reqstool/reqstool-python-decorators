#!/usr/bin/env python3
# Copyright © LFV
"""Self-apply the decorator processor to this repo's own src/tests, producing
build/reqstool/annotations.yml for `reqstool status` to consume."""

from reqstool_python_decorators.processors.decorator_processor import DecoratorProcessor

if __name__ == "__main__":
    DecoratorProcessor().process_decorated_data(
        # tests/resources holds fixture files with intentionally-fake REQ_*/SVC_* IDs
        # (used by tests/e2e to exercise the processor against real decorator syntax) --
        # excluded here so they don't pollute this repo's own traceability data.
        # tests/integration is omitted entirely: it's currently just empty __init__.py
        # stubs, add it back once real integration tests land there.
        path_to_python_files=["src", "tests/unit", "tests/e2e"],
        output_file="build/reqstool/annotations.yml",
    )
