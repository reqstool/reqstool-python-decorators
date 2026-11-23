import os
import subprocess
import sys
from pathlib import PureWindowsPath

import pytest
from reqstool_python_decorators.decorators.decorators import SVCs
from reqstool_python_decorators.processors.decorator_processor import DecoratorProcessor
from ruamel.yaml import YAML


@pytest.fixture
def process_decorator_instance():
    return DecoratorProcessor()


# ---------------------------------------------------------------------------
# find_python_files
# ---------------------------------------------------------------------------


@SVCs("SVC_DECORATORS_002")
def test_find_python_files(process_decorator_instance: DecoratorProcessor, tmp_path):
    (tmp_path / "pythonfile.py").write_text("content")
    result = process_decorator_instance.find_python_files(tmp_path)
    assert result == [str(tmp_path / "pythonfile.py")]


@SVCs("SVC_DECORATORS_002")
def test_find_python_files_empty_dir(process_decorator_instance: DecoratorProcessor, tmp_path):
    result = process_decorator_instance.find_python_files(tmp_path)
    assert result == []


@SVCs("SVC_DECORATORS_002")
def test_find_python_files_nested(process_decorator_instance: DecoratorProcessor, tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nested.py").write_text("content")
    result = process_decorator_instance.find_python_files(tmp_path)
    assert str(sub / "nested.py") in result


@SVCs("SVC_DECORATORS_002")
def test_find_python_files_ignores_non_py(process_decorator_instance: DecoratorProcessor, tmp_path):
    (tmp_path / "readme.txt").write_text("content")
    result = process_decorator_instance.find_python_files(tmp_path)
    assert result == []


# ---------------------------------------------------------------------------
# get_functions_and_classes
# ---------------------------------------------------------------------------


@SVCs("SVC_DECORATORS_002")
def test_get_functions_and_classes(process_decorator_instance: DecoratorProcessor, tmp_path):
    file_path = tmp_path / "test_file.py"
    file_path.write_text('@SVCs("SVC_001")\nclass Test:\n  pass')
    process_decorator_instance.get_functions_and_classes(file_path, ["SVCs"])
    assert process_decorator_instance.req_svc_results[0]["name"] == "Test"
    assert process_decorator_instance.req_svc_results[0]["decorators"][0]["args"][0] == "SVC_001"
    assert process_decorator_instance.req_svc_results[0]["decorators"][0]["name"] == "SVCs"
    assert process_decorator_instance.req_svc_results[0]["elementKind"] == "CLASS"


@SVCs("SVC_DECORATORS_002")
def test_get_functions_and_classes_function_def(process_decorator_instance: DecoratorProcessor, tmp_path):
    file_path = tmp_path / "f.py"
    file_path.write_text('@Requirements("REQ_001")\ndef my_func():\n    pass')
    process_decorator_instance.get_functions_and_classes(file_path, ["Requirements"])
    assert len(process_decorator_instance.req_svc_results) == 1
    result = process_decorator_instance.req_svc_results[0]
    assert result["name"] == "my_func"
    assert result["elementKind"] == "FUNCTION"


@SVCs("SVC_DECORATORS_002")
def test_get_functions_and_classes_async_function_def(process_decorator_instance: DecoratorProcessor, tmp_path):
    file_path = tmp_path / "af.py"
    file_path.write_text('@Requirements("REQ_001")\nasync def my_async():\n    pass')
    process_decorator_instance.get_functions_and_classes(file_path, ["Requirements"])
    assert len(process_decorator_instance.req_svc_results) == 1
    result = process_decorator_instance.req_svc_results[0]
    assert result["name"] == "my_async"
    assert result["elementKind"] == "ASYNCFUNCTION"


@SVCs("SVC_DECORATORS_002")
def test_get_functions_and_classes_multiple_args(process_decorator_instance: DecoratorProcessor, tmp_path):
    file_path = tmp_path / "m.py"
    file_path.write_text('@Requirements("A", "B")\ndef func():\n    pass')
    process_decorator_instance.get_functions_and_classes(file_path, ["Requirements"])
    args = process_decorator_instance.req_svc_results[0]["decorators"][0]["args"]
    assert args == ["A", "B"]


@SVCs("SVC_DECORATORS_002")
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


@SVCs("SVC_DECORATORS_002")
def test_get_functions_and_classes_no_match(process_decorator_instance: DecoratorProcessor, tmp_path):
    file_path = tmp_path / "n.py"
    file_path.write_text('@OtherDecorator("X")\ndef func():\n    pass')
    process_decorator_instance.get_functions_and_classes(file_path, ["Requirements"])
    assert process_decorator_instance.req_svc_results == []


@SVCs("SVC_DECORATORS_002")
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


@SVCs("SVC_DECORATORS_002")
def test_map_type_known_type(process_decorator_instance: DecoratorProcessor):
    map_funcion = process_decorator_instance.map_type("FUNCTION")
    map_asyncfunction = process_decorator_instance.map_type("ASYNCFUNCTION")
    assert map_funcion == "METHOD"
    assert map_asyncfunction == "METHOD"


@SVCs("SVC_DECORATORS_002")
def test_map_type_unknown_type(process_decorator_instance: DecoratorProcessor):
    result = process_decorator_instance.map_type("CLASS")
    assert result == "CLASS"


# ---------------------------------------------------------------------------
# format_results
# ---------------------------------------------------------------------------


@SVCs("SVC_DECORATORS_002")
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


@SVCs("SVC_DECORATORS_002")
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


@SVCs("SVC_DECORATORS_002")
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


@SVCs("SVC_DECORATORS_002")
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


@SVCs("SVC_DECORATORS_003")
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


@SVCs("SVC_DECORATORS_003")
def test_create_dir_from_path_creates_dir(process_decorator_instance: DecoratorProcessor, tmp_path):
    new_dir = tmp_path / "new_subdir"
    filepath = str(new_dir / "output.yml")
    process_decorator_instance.create_dir_from_path(filepath)
    assert new_dir.exists()


@SVCs("SVC_DECORATORS_003")
def test_create_dir_from_path_existing_dir(process_decorator_instance: DecoratorProcessor, tmp_path):
    filepath = str(tmp_path / "output.yml")
    # tmp_path already exists — should not raise
    process_decorator_instance.create_dir_from_path(filepath)
    assert tmp_path.exists()


# ---------------------------------------------------------------------------
# process_decorated_data
# ---------------------------------------------------------------------------


@SVCs("SVC_DECORATORS_002", "SVC_DECORATORS_003")
def test_process_decorated_data_produces_yaml(process_decorator_instance: DecoratorProcessor, tmp_path):
    src_file = tmp_path / "src" / "app.py"
    src_file.parent.mkdir()
    src_file.write_text('@Requirements("REQ_001")\ndef my_func():\n    pass\n')

    output_file = tmp_path / "out" / "annotations.yml"
    process_decorator_instance.process_decorated_data(
        path_to_python_files=[str(src_file.parent)], output_file=output_file
    )

    assert output_file.exists()


@SVCs("SVC_DECORATORS_002", "SVC_DECORATORS_003")
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


@SVCs("SVC_DECORATORS_002", "SVC_DECORATORS_003")
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


# ---------------------------------------------------------------------------
# non-ASCII sources / platform locale encoding
# ---------------------------------------------------------------------------

# "Đ" is C4 90 in UTF-8; 0x90 is undefined in cp1252, so a locale-decoded read fails on Windows,
# and any non-ASCII byte fails under an ASCII locale on Linux and macOS.
_NON_ASCII_SOURCE = '# Đ non-ASCII comment\n@Requirements("REQ_001")\ndef my_func():\n    """Đ"""\n'

_RUN_PROCESSOR = (
    "import sys\n"
    "from reqstool_python_decorators.processors.decorator_processor import DecoratorProcessor\n"
    "DecoratorProcessor().process_decorated_data([sys.argv[1]], output_file=sys.argv[2])\n"
)


@SVCs("SVC_DECORATORS_002", "SVC_DECORATORS_003")
def test_process_decorated_data_non_ascii_source_with_non_utf8_locale(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "mod.py").write_bytes(_NON_ASCII_SOURCE.encode("utf-8"))
    output_file = tmp_path / "out" / "annotations.yml"

    # Run in a child process with UTF-8 mode off and a legacy locale to mimic a default Windows setup.
    env = {
        **os.environ,
        "PYTHONUTF8": "0",
        "PYTHONCOERCECLOCALE": "0",
        "PYTHONIOENCODING": "utf-8",
        "LC_ALL": "C",
        "LANG": "C",
    }
    result = subprocess.run(
        [sys.executable, "-c", _RUN_PROCESSOR, str(src_dir), str(output_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    data = YAML().load(output_file.read_text(encoding="utf-8"))
    assert [
        e["fullyQualifiedName"].rsplit(".", 1)[-1]
        for e in data["requirement_annotations"]["implementations"]["REQ_001"]
    ] == ["my_func"]


@SVCs("SVC_DECORATORS_002")
def test_get_functions_and_classes_honours_pep263_encoding_declaration(
    process_decorator_instance: DecoratorProcessor, tmp_path
):
    src_file = tmp_path / "latin1_mod.py"
    src_file.write_bytes(
        '# -*- coding: latin-1 -*-\n# é\n@Requirements("REQ_001")\ndef my_func():\n    pass\n'.encode("latin-1")
    )

    process_decorator_instance.get_functions_and_classes(src_file, ["Requirements"])

    assert [r["name"] for r in process_decorator_instance.req_svc_results] == ["my_func"]


# ---------------------------------------------------------------------------
# Windows-style paths in fullyQualifiedName
# ---------------------------------------------------------------------------


@SVCs("SVC_DECORATORS_002")
def test_fully_qualified_name_uses_dots_for_windows_path_separators(
    process_decorator_instance: DecoratorProcessor, tmp_path, monkeypatch
):
    # os.walk/os.path.join yield "src\\pkg\\mod.py" on Windows; backslashes used to survive into the name.
    package = tmp_path / "src" / "pkg"
    package.mkdir(parents=True)
    (package / "mod.py").write_text('@Requirements("REQ_001")\ndef my_func():\n    pass\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    process_decorator_instance.get_functions_and_classes(PureWindowsPath("src\\pkg\\mod.py"), ["Requirements"])
    formatted = process_decorator_instance.format_results(process_decorator_instance.req_svc_results)

    assert formatted["requirement_annotations"]["implementations"]["REQ_001"] == [
        {"elementKind": "METHOD", "fullyQualifiedName": "src.pkg.mod.my_func"}
    ]
