import pytest
from reqstool_python_decorators.processors.decorator_processor import DecoratorProcessor
from ruamel.yaml import YAML


@pytest.fixture
def process_decorator_instance():
    return DecoratorProcessor()


# ---------------------------------------------------------------------------
# find_python_files
# ---------------------------------------------------------------------------


def test_find_python_files(process_decorator_instance: DecoratorProcessor, tmp_path):
    (tmp_path / "pythonfile.py").write_text("content")
    result = process_decorator_instance.find_python_files(tmp_path)
    assert result == [str(tmp_path / "pythonfile.py")]


def test_find_python_files_empty_dir(process_decorator_instance: DecoratorProcessor, tmp_path):
    result = process_decorator_instance.find_python_files(tmp_path)
    assert result == []


def test_find_python_files_nested(process_decorator_instance: DecoratorProcessor, tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nested.py").write_text("content")
    result = process_decorator_instance.find_python_files(tmp_path)
    assert str(sub / "nested.py") in result


def test_find_python_files_ignores_non_py(process_decorator_instance: DecoratorProcessor, tmp_path):
    (tmp_path / "readme.txt").write_text("content")
    result = process_decorator_instance.find_python_files(tmp_path)
    assert result == []


# ---------------------------------------------------------------------------
# get_functions_and_classes
# ---------------------------------------------------------------------------


def test_get_functions_and_classes(process_decorator_instance: DecoratorProcessor, tmp_path):
    file_path = tmp_path / "test_file.py"
    file_path.write_text('@SVCs("SVC_001")\nclass Test:\n  pass')
    process_decorator_instance.get_functions_and_classes(file_path, ["SVCs"])
    assert process_decorator_instance.req_svc_results[0]["name"] == "Test"
    assert process_decorator_instance.req_svc_results[0]["decorators"][0]["args"][0] == "SVC_001"
    assert process_decorator_instance.req_svc_results[0]["decorators"][0]["name"] == "SVCs"
    assert process_decorator_instance.req_svc_results[0]["elementKind"] == "CLASS"


def test_get_functions_and_classes_function_def(process_decorator_instance: DecoratorProcessor, tmp_path):
    file_path = tmp_path / "f.py"
    file_path.write_text('@Requirements("REQ_001")\ndef my_func():\n    pass')
    process_decorator_instance.get_functions_and_classes(file_path, ["Requirements"])
    assert len(process_decorator_instance.req_svc_results) == 1
    result = process_decorator_instance.req_svc_results[0]
    assert result["name"] == "my_func"
    assert result["elementKind"] == "FUNCTION"


def test_get_functions_and_classes_async_function_def(process_decorator_instance: DecoratorProcessor, tmp_path):
    file_path = tmp_path / "af.py"
    file_path.write_text('@Requirements("REQ_001")\nasync def my_async():\n    pass')
    process_decorator_instance.get_functions_and_classes(file_path, ["Requirements"])
    assert len(process_decorator_instance.req_svc_results) == 1
    result = process_decorator_instance.req_svc_results[0]
    assert result["name"] == "my_async"
    assert result["elementKind"] == "ASYNCFUNCTION"


def test_get_functions_and_classes_multiple_args(process_decorator_instance: DecoratorProcessor, tmp_path):
    file_path = tmp_path / "m.py"
    file_path.write_text('@Requirements("A", "B")\ndef func():\n    pass')
    process_decorator_instance.get_functions_and_classes(file_path, ["Requirements"])
    args = process_decorator_instance.req_svc_results[0]["decorators"][0]["args"]
    assert args == ["A", "B"]


@pytest.mark.parametrize(
    "code,expected_kind",
    [
        ('@Requirements("REQ_001")\ndef func(): pass', "FUNCTION"),
        ('@Requirements("REQ_001")\nasync def func(): pass', "ASYNCFUNCTION"),
        ('@Requirements("REQ_001")\nclass MyClass: pass', "CLASS"),
    ],
)
def test_get_functions_and_classes_element_kind(
    process_decorator_instance: DecoratorProcessor, tmp_path, code, expected_kind
):
    """Fix 4: elementKind must be derived from __class__.__name__, not CPython repr."""
    f = tmp_path / "f.py"
    f.write_text(code)
    process_decorator_instance.get_functions_and_classes(f, ["Requirements"])
    assert process_decorator_instance.req_svc_results[0]["elementKind"] == expected_kind


def test_get_functions_and_classes_no_match(process_decorator_instance: DecoratorProcessor, tmp_path):
    file_path = tmp_path / "n.py"
    file_path.write_text('@OtherDecorator("X")\ndef func():\n    pass')
    process_decorator_instance.get_functions_and_classes(file_path, ["Requirements"])
    assert process_decorator_instance.req_svc_results == []


def test_get_functions_and_classes_multiple_decorators_on_func(
    process_decorator_instance: DecoratorProcessor, tmp_path
):
    file_path = tmp_path / "md.py"
    code = '@Requirements("REQ_001")\n@SVCs("SVC_001")\ndef func():\n    pass'
    file_path.write_text(code)
    process_decorator_instance.get_functions_and_classes(file_path, ["Requirements", "SVCs"])
    assert len(process_decorator_instance.req_svc_results) == 1
    names = [d["name"] for d in process_decorator_instance.req_svc_results[0]["decorators"]]
    assert "Requirements" in names
    assert "SVCs" in names


# ---------------------------------------------------------------------------
# map_type
# ---------------------------------------------------------------------------


def test_map_type_known_type(process_decorator_instance: DecoratorProcessor):
    map_funcion = process_decorator_instance.map_type("FUNCTION")
    map_asyncfunction = process_decorator_instance.map_type("ASYNCFUNCTION")
    assert map_funcion == "METHOD"
    assert map_asyncfunction == "METHOD"


def test_map_type_unknown_type(process_decorator_instance: DecoratorProcessor):
    result = process_decorator_instance.map_type("CLASS")
    assert result == "CLASS"


# ---------------------------------------------------------------------------
# format_results
# ---------------------------------------------------------------------------


def test_format_results_implementations(process_decorator_instance: DecoratorProcessor):
    results = [
        {
            "fullyQualifiedName": "my.module.py",
            "elementKind": "FUNCTION",
            "name": "func",
            "decorators": [{"name": "Requirements", "args": ["REQ_001"]}],
        }
    ]
    data = process_decorator_instance.format_results(results)
    assert "REQ_001" in data["requirement_annotations"]["implementations"]


def test_format_results_tests(process_decorator_instance: DecoratorProcessor):
    results = [
        {
            "fullyQualifiedName": "my.module.py",
            "elementKind": "FUNCTION",
            "name": "test_func",
            "decorators": [{"name": "SVCs", "args": ["SVC_001"]}],
        }
    ]
    data = process_decorator_instance.format_results(results)
    assert "SVC_001" in data["requirement_annotations"]["tests"]


def test_format_results_multiple_ids(process_decorator_instance: DecoratorProcessor):
    results = [
        {
            "fullyQualifiedName": "my.module.py",
            "elementKind": "FUNCTION",
            "name": "func",
            "decorators": [{"name": "Requirements", "args": ["REQ_001", "REQ_002"]}],
        }
    ]
    data = process_decorator_instance.format_results(results)
    impls = data["requirement_annotations"]["implementations"]
    assert "REQ_001" in impls
    assert "REQ_002" in impls


def test_format_results_fully_qualified_name(process_decorator_instance: DecoratorProcessor):
    results = [
        {
            "fullyQualifiedName": "path.to.module.py",
            "elementKind": "FUNCTION",
            "name": "my_func",
            "decorators": [{"name": "Requirements", "args": ["REQ_001"]}],
        }
    ]
    data = process_decorator_instance.format_results(results)
    entry = data["requirement_annotations"]["implementations"]["REQ_001"][0]
    assert entry["fullyQualifiedName"].endswith(".my_func")


# ---------------------------------------------------------------------------
# write_to_yaml
# ---------------------------------------------------------------------------


def test_write_to_yaml(process_decorator_instance: DecoratorProcessor, tmp_path):
    yaml_language_server = "# yaml-language-server: $schema=https://raw.githubusercontent.com/reqstool/reqstool-client/main/src/reqstool/resources/schemas/v1/annotations.schema.json\n"  # noqa: E501

    test_output_file = tmp_path / "test_output.yml"
    sample_formatted_data = """
                            requirement_annotations:
                                implementations:
                                    REQ_101:
                                        - elementKind: "CLASS"
                                            fullyQualifiedName: "com.example.RequirementsExample"
                                    """
    process_decorator_instance.write_to_yaml(output_file=test_output_file, formatted_data=sample_formatted_data)

    assert test_output_file.exists()

    with open(test_output_file, "r") as test_file:
        assert yaml_language_server in test_file.read()
        test_file.seek(0)
        yaml = YAML()
        loaded_data = yaml.load(test_file)
        assert sample_formatted_data == loaded_data


# ---------------------------------------------------------------------------
# create_dir_from_path
# ---------------------------------------------------------------------------


def test_create_dir_from_path_creates_dir(process_decorator_instance: DecoratorProcessor, tmp_path):
    new_dir = tmp_path / "new_subdir"
    filepath = str(new_dir / "output.yml")
    process_decorator_instance.create_dir_from_path(filepath)
    assert new_dir.exists()


def test_create_dir_from_path_existing_dir(process_decorator_instance: DecoratorProcessor, tmp_path):
    filepath = str(tmp_path / "output.yml")
    # tmp_path already exists — should not raise
    process_decorator_instance.create_dir_from_path(filepath)
    assert tmp_path.exists()


# ---------------------------------------------------------------------------
# process_decorated_data
# ---------------------------------------------------------------------------


def test_process_decorated_data_produces_yaml(process_decorator_instance: DecoratorProcessor, tmp_path):
    src_file = tmp_path / "src" / "app.py"
    src_file.parent.mkdir()
    src_file.write_text('@Requirements("REQ_001")\ndef my_func():\n    pass\n')

    output_file = tmp_path / "out" / "annotations.yml"
    process_decorator_instance.process_decorated_data(
        path_to_python_files=[str(src_file.parent)], output_file=output_file
    )

    assert output_file.exists()


def test_process_decorated_data_correct_structure(process_decorator_instance: DecoratorProcessor, tmp_path):
    src_file = tmp_path / "src" / "app.py"
    src_file.parent.mkdir()
    src_file.write_text('@Requirements("REQ_001")\ndef my_func():\n    pass\n')

    output_file = tmp_path / "out" / "annotations.yml"
    process_decorator_instance.process_decorated_data(
        path_to_python_files=[str(src_file.parent)], output_file=output_file
    )

    yaml = YAML()
    with open(output_file) as f:
        data = yaml.load(f)

    assert "requirement_annotations" in data
    assert "REQ_001" in data["requirement_annotations"]["implementations"]


def test_process_decorated_data_no_state_accumulation(process_decorator_instance: DecoratorProcessor, tmp_path):
    src_file = tmp_path / "src" / "app.py"
    src_file.parent.mkdir()
    src_file.write_text('@Requirements("REQ_001")\ndef my_func():\n    pass\n')

    output_file = tmp_path / "out" / "annotations.yml"

    # Call twice
    process_decorator_instance.process_decorated_data(
        path_to_python_files=[str(src_file.parent)], output_file=output_file
    )
    process_decorator_instance.process_decorated_data(
        path_to_python_files=[str(src_file.parent)], output_file=output_file
    )

    yaml = YAML()
    with open(output_file) as f:
        data = yaml.load(f)

    # Should have exactly 1 entry, not 2 due to state accumulation
    entries = data["requirement_annotations"]["implementations"]["REQ_001"]
    assert len(entries) == 1
