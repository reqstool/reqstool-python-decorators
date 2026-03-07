[![Commit Activity](https://img.shields.io/github/commit-activity/m/reqstool/reqstool-python-decorators?label=commits&style=for-the-badge)](https://github.com/reqstool/reqstool-python-decorators/pulse)
[![GitHub Issues](https://img.shields.io/github/issues/reqstool/reqstool-python-decorators?style=for-the-badge&logo=github)](https://github.com/reqstool/reqstool-python-decorators/issues)
[![License](https://img.shields.io/github/license/reqstool/reqstool-python-decorators?style=for-the-badge&logo=opensourceinitiative)](https://opensource.org/license/mit/)
[![Build](https://img.shields.io/github/actions/workflow/status/reqstool/reqstool-python-decorators/build.yml?style=for-the-badge&logo=github)](https://github.com/reqstool/reqstool-python-decorators/actions/workflows/build.yml)
[![Documentation](https://img.shields.io/badge/Documentation-blue?style=for-the-badge&link=docs)](https://reqstool.github.io)

# Reqstool Python Decorators

Python decorators for [reqstool](https://github.com/reqstool/reqstool-client) requirements traceability. Provides `@Requirements` and `@SVCs` decorators for linking Python code to requirements and software verification cases.

## Requirements

- Python >= 3.13

## Installation

```bash
pip install reqstool-python-decorators
```

## Usage

```python
from reqstool_python_decorators.decorators.decorators import Requirements, SVCs

@Requirements("REQ_111", "REQ_222")
def somefunction():
    pass

@SVCs("SVC_111", "SVC_222")
def test_somefunction():
    pass
```

### Processor

```python
from reqstool_python_decorators.processors.decorator_processor import DecoratorProcessor

# Collect decorators and generate annotations.yml
process_decorated_data(path_to_python_files, output_file)
```

Used together with the [Hatch Plugin](https://github.com/reqstool/reqstool-python-hatch-plugin) or [Poetry Plugin](https://github.com/reqstool/reqstool-python-poetry-plugin).

## Documentation

Full documentation can be found [here](https://reqstool.github.io).

## Contributing

See the organization-wide [CONTRIBUTING.md](https://github.com/reqstool/.github/blob/main/CONTRIBUTING.md).

## License

MIT License.
