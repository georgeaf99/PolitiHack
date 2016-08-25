# PolitiHack
A chat bot that keeps you connected to important political decisions


## Execution

1. Update the project configuration, `config.json`
2. Check and install the requirements by running reqs.sh
3. Set the environment vars and execute by running run.sh

## Development

System requirements:

* Unix-like environment
* Python 3

How to run static analysis: `pylint -E $(find . -type f -name "*.py")`

Basic Style Guide:

1. Use `import <full namespace module name> as <module name>` all module imports
2. Use `from <full namespace module name> import <class>` for importing classes from other modules
3. Do not import functions or variables from other modules, use `<module name>.(var|func)` instead
