TLDR: "pytest --log-disable=__name__"

To run tests:
- Ensure you have run "poetry install" to install the required dependencies
- Run "pytest" from the root directory of the project
- It is highly recommended to run "pytest --log-disable=__name__" to disable logging during tests
- This is recommended due to some tests specifically target logging output