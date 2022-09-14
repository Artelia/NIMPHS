# Contributing

## Questions

For general questions about the project, software usage or Blender related issues please use
the [Discussions](https://github.com/Artelia/NIMPHS/discussions) tab for that.

## Bug report

If you encounter a bug using NIMPHS, please open a new issue. Do not hesitate to be overly
descriptive so that we can reproduce the bug. Screenshots, sample files, tracebacks, etc. are
welcomed.

## Feature requests

We encourage users to propose new ideas in order to improve NIMPHS. For that, please first open a new
issue to describe what could be improved, added or changed. Do not hesitate to illustrate the desired
outcomes with schemas, screenshots, documentation, etc.

## Licensing

If you plan to add new data or code to NIMPHS, please make sure its licence is compatible with the
licence we use.

-------------------------------------------------------------------------------------------------------------

## Development environment and practices

Please refer to the information given in the [developers manual](https://artelia.github.io/NIMPHS/developers/index.html).

## Contributing through Github

To submit new code to NIMPHS, you first need to fork the GitHub repository. Then, clone the forked repository
to your computer. Create a new branch following our [branch naming conventions](#branch-naming-conventions) in your
local repository.

Next, add your new features in your local branch. Once you are ready to submit your code, please open a new pull request.

## Branch naming conventions

When creating a new branch, please name it as indicated here:

* `doc/`: additions or changes in the documentation
* `feat/`: new feature or significant addition
* `fix/`: bug fixes or minor changes
* `maint/`: for maintenance tasks
* `release/`: for new releases

Use hyphens to separate words in the branch title.
Example: `feat/my-new-feature`

## Style checking

We use style checking tools to verify that new code always meet our [coding style standards](https://artelia.github.io/NIMPHS/developers/introduction.html#coding-style).
You can run a test using:

```shell
pip install pre-commit
pre-commint run --all-files
```

## Unit testing

Run the test suite. Here is an example to run the test suite for Blender 3.2.1:

```shell
python -m scripts.run_tests.py -b "3.2.1"
```

For more information, please refer to the [corresponding section](https://artelia.github.io/NIMPHS/developers/development_environment.html#unit-tests)
in the developers manual.

## Documentation

Our documentation is built using the python package sphinx.
When running commands to build the documentation, please make sure you are under the `docs/` folder.

### Style checking

You can check for misspellings using this command:

```shell
make spelling
```

### Code documentation

The code documentation is automatically generated from docstrings written in the python files.
Run this command to generate / update code documentation:

```shell
sphinx-apidoc -t "_templates/" --implicit-namespaces -d 1 -f -M -T -o source/developers/code/ ../nimphs "/*auto_load.py" "/*serafin.py" "/*checkdeps.py"
```

### Build documentation

Run this command to build the documentation:

```shell
make html
```

It is then available under `docs/_build/html/index.html` (open this file in a web browser).