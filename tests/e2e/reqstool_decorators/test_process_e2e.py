# Copyright © LFV

import os

import pytest
from reqstool_python_decorators.decorators.decorators import SVCs
from reqstool_python_decorators.processors.decorator_processor import DecoratorProcessor
from ruamel.yaml import YAML


@pytest.mark.e2e
@SVCs("SVC_DECORATORS_002", "SVC_DECORATORS_003")
def test_process_decorated_data_against_fixture_files(tmp_path):
    """Runs the full pipeline against tests/resources/test_decorators, real
    @Requirements/@SVCs-decorated fixture files rather than synthetic ASTs."""

    tests_rootdir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    fixtures_dir = os.path.join(tests_rootdir, "resources", "test_decorators")
    output_file = tmp_path / "annotations.yml"

    DecoratorProcessor().process_decorated_data(path_to_python_files=[fixtures_dir], output_file=output_file)

    yaml = YAML()
    with open(output_file) as f:
        data = yaml.load(f)

    implementations = data["requirement_annotations"]["implementations"]
    tests = data["requirement_annotations"]["tests"]

    assert {"REQ_001", "REQ_222", "REQ_333", "REQ_444"} <= implementations.keys()
    assert {"SVC_999", "SVC_123"} <= tests.keys()

    assert implementations["REQ_001"][0]["elementKind"] == "CLASS"
    assert implementations["REQ_333"][0]["elementKind"] == "METHOD"
    assert implementations["REQ_444"][0]["elementKind"] == "METHOD"

    # SVC_999 is declared on both test functions in svc_decorators.py
    assert len(tests["SVC_999"]) == 2
