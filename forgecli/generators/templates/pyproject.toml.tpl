[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{{COMMAND_NAME}}"
version = "{{VERSION}}"
description = "{{DESCRIPTION}}"
readme = "README.md"
requires-python = "{{PYTHON_VERSION}}"
license = {text = "{{LICENSE}}"}
authors = [{name = "{{AUTHOR}}"}]
keywords = {{TAGS_PY_LIST}}
dependencies = [
    "rich>=13.7.0",
    "pyfiglet>=1.0.2",
    "questionary>=2.0.1",
]

[project.scripts]
{{COMMAND_NAME}} = "main:main"

[tool.setuptools]
py-modules = ["main", "banner", "ui", "utils", "theme", "installer", "updater", "commands"]