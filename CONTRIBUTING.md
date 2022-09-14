# Contributing

## Questions

For general questions about the project, software usage or Blender related issues please use
the [Discussions](https://github.com/Artelia/NIMPHS/discussions) tab for that.

## Bug report

If you encouter a bug using NIMPHS, please open a new issue. Do not hesistate to be overly
descriptive so that we can reproduce the bug. Screenshots, sample files, tracebacks, etc. are
welcomed.

## Feature requests

We encourage users to propose new ideas in order to improve NIMPHS. For that, please first open a new
issue to describe what could be improved, added or changed. Do not hesistate to illustrate the desired
outcomes with schemas, screenshots, documentation, etc.

## Licensing

If you plan to add new data or code to NIMPHS, please make sure it is compatible with the GNU GPL v3.

-------------------------------------------------------------------------------------------------------------

## Development environment and practices

Please refer to the information given in the [developers manual](https://artelia.github.io/NIMPHS/developers/index.html).

## Contributing through Github

To submit new code to NIMPHS, you first need to fork the GitHub repository. Then, clone the forked repository
to you computer. Create a new branch following our [branch naming conventions](#branch-naming-conventions) in your
local repository.

Next, add your new features in your local branch. Once you are ready to submit your code, please open a new pull request.

## Branch naming conventions

When creating a new branch, please name it as indicated here:

* `doc/`: additions or changes in the documentation
* `feat/`: new feature or significant addition
* `fix/`: bug fixes or minor changes
* `maint/`: for maintainance tasks
* `release/`: for new releases

## Style checking

We use style checking tools to verify that new code always meet our [coding style standards](https://artelia.github.io/NIMPHS/developers/introduction.html#coding-style).
You can run a test using:

```bash
pip install pre-commit
pre-commint run --all-files
```

## Unit testing

Run the test suite. Here is an example to run the test suite for Blender 3.2.1:

```bash
python -m scripts.run_tests.py -b "3.2.1"
```

For more information, please refer to the [corresponding section](https://artelia.github.io/NIMPHS/developers/development_environment.html#unit-tests)
in the developers manual.