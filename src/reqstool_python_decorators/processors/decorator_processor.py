# Copyright © LFV

from enum import Enum, unique
import os
from typing import ReadOnly, TypedDict
from ruamel.yaml import YAML
import ast


@unique
class DECORATOR_TYPES(Enum):
    FUNCTION = ("FUNCTION", "METHOD")
    ASYNCFUNCTION = ("ASYNCFUNCTION", "METHOD")

    def __init__(self, from_value, to_value):
        self.from_value = from_value
        self.to_value = to_value

    def get_from_to(self):
        return f"from: {self.from_value}, to: {self.to_value}"


class DecoratorInfo(TypedDict):
    name: ReadOnly[str]
    args: ReadOnly[list[str]]


class ElementResult(TypedDict):
    fullyQualifiedName: ReadOnly[str]
    elementKind: ReadOnly[str]
    name: ReadOnly[str]
    decorators: ReadOnly[list[DecoratorInfo]]


type Results = list[ElementResult]


class DecoratorProcessor:
    """
    A class for collecting and processing Requirements and SVCs annotations on functions and classes in a directory.

    Attributes:
    - `decorators_to_search` (list): List of decorator names to search.
    - `reqsvc_yaml_path` (str): Path for Requirements and SVC annotations YAML.

    - `yaml_language_server` (str): YAML language server information.
    """

    decorators_to_search = ["Requirements", "SVCs"]

    yaml_language_server = "# yaml-language-server: $schema=https://raw.githubusercontent.com/reqstool/reqstool-client/main/src/reqstool/resources/schemas/v1/annotations.schema.json\n"  # noqa: E501

    def __init__(self, *args, **kwargs):
        """
        Initialize the ProcessDecorator instance.

        Parameters:
        - `*args`: Variable length argument list.
        - `**kwargs`: Arbitrary keyword arguments.

        Attributes:
        - `req_svc_results` (list): List to store results of Requirements and SVCs annotations.

        """
        super().__init__(*args, **kwargs)
        self.req_svc_results: Results = []

    def find_python_files(self, directory) -> list[str]:
        """
        Find Python files in the given directory.

        Parameters:
        - `directory` (str): The directory to search for Python files.

        Returns:
        - `python_files` (list): List of Python files found in the directory.
        """
        python_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        return python_files

    def get_functions_and_classes(self, file_path, decorator_names) -> None:
        """
        Get information about functions and classes, if annotated with "Requirements" or "SVCs":
        decorator filepath, elementKind, name and decorators is saved to list that is returned.

        Parameters:
        - `file_path` (str): The path to the Python file.
        - `decorator_names` (list): List of decorator names to search for.

        Returns:
        - `results` (list): List of dictionaries containing information about functions and classes.

        Each dictionary includes:
            - `fullyQualifiedName` (str): The fully qualified name of the file.
            - `elementKind` (str): The kind of the element (e.g., METHOD, CLASS).
            - `name` (str): The name of the function or class.
            - `decorators` (list): List of dictionaries with decorator info including name and arguments e.g. "REQ_001".
        """
        with open(file_path, "r") as file:
            tree = ast.parse(file.read(), filename=file_path)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                decorators_info: list[DecoratorInfo] = []
                for decorator_node in getattr(node, "decorator_list", []):
                    if isinstance(decorator_node, ast.Call) and isinstance(decorator_node.func, ast.Name):
                        decorator_name = decorator_node.func.id
                        args = [arg.value for arg in decorator_node.args if isinstance(arg, ast.Constant)]
                        decorators_info.append({"name": decorator_name, "args": args})

                if any(decorator_info["name"] in decorator_names for decorator_info in decorators_info):
                    self.req_svc_results.append(
                        {
                            "fullyQualifiedName": str(file_path).replace("/", "."),
                            "elementKind": node.__class__.__name__[:-3].upper(),
                            "name": node.name,
                            "decorators": decorators_info,
                        }
                    )

    def write_to_yaml(self, output_file, formatted_data) -> None:
        """
        Write formatted data to a YAML file.

        Parameters:
        - `output_file` (str): The path to the output YAML file.
        - `formatted_data` (dict): The formatted data to be written to the YAML file.

        Writes the formatted data to the specified YAML file.
        The YAML file includes a header from the YAML language server.

        Example:
        ```python
        instance = ProcessDecorator()
        data = {"version": "9.9.9", "requirement_annotations": {"tests": {
            "requirement_id": [{"elementKind": "METHOD", "fullyQualifiedName": "example_module.example_function"}]}}}
        instance.write_to_yaml("output_file.yml", data)
        ```
        """
        with open(output_file, "w") as yaml_file:
            yaml = YAML()
            yaml.default_flow_style = False
            yaml_file.write(self.yaml_language_server)
            yaml.dump(formatted_data, yaml_file)

    def map_type(self, input_str) -> str:
        mapping = {item.from_value: item.to_value for item in DECORATOR_TYPES}
        return mapping.get(input_str, input_str)

    def format_results(self, results: Results) -> dict:
        """
        Format the collected results into a structured data format for YAML.

        Parameters:
        - `results` (list): List of dictionaries containing information about functions and classes.

        Returns:
        - `formatted_data` (dict): Formatted data in a structured `yaml_language_server` compatible format.

        This function formats a list of decorated data into the structure required by the `yaml_language_server`.
        It includes version information, requirement annotations, and relevant element information.
        """

        formatted_data = {}
        implementations = {}
        tests = {}
        requirement_annotations = {"implementations": implementations, "tests": tests}
        formatted_data["requirement_annotations"] = requirement_annotations

        for result in results:
            for decorator_info in result["decorators"]:
                ids = decorator_info["args"]
                decorator_name = decorator_info["name"]

                for id in ids:
                    target_dict = implementations if decorator_name == "Requirements" else tests
                    if id not in target_dict:
                        target_dict[id] = []

                    target_dict[id].append(
                        {
                            "elementKind": self.map_type(result["elementKind"]),
                            "fullyQualifiedName": result["fullyQualifiedName"][:-3] + "." + result["name"],
                        }
                    )

        return formatted_data

    def create_dir_from_path(self, filepath: str) -> None:
        """
        Creates directory of provided filepath if it does not exists

        Parameters:
        - `filepath` (str): Filepath to check and create directory from.
        """
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def process_decorated_data(
        self, path_to_python_files: str, output_file: str = "build/reqstool/annotations.yml"
    ) -> None:
        """
        "Main" function, runs all functions resulting in  a yaml file containing decorated data.

        Parameters:
        - `path_to_python_files` (list): List of directories containing Python files.
        - `output_file` (str): Set path for output file, defaults to build/annotations.yml

        This method takes a list of directories containing Python files, collects decorated data from these files,
        formats the collected data, and writes the formatted results to YAML file for Requirements and SVCs annotations.
        """

        self.req_svc_results = []

        for path in path_to_python_files:
            python_files = self.find_python_files(directory=path)
            for file_path in python_files:
                self.get_functions_and_classes(file_path=file_path, decorator_names=self.decorators_to_search)

        formatted_reqsvc_data = self.format_results(results=self.req_svc_results)

        self.create_dir_from_path(output_file)
        self.write_to_yaml(output_file=output_file, formatted_data=formatted_reqsvc_data)
