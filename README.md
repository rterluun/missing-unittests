# missing-unittests
<!-- markdownlint-disable MD013-->

## How to use

This is a simple utility to show which functions in your codebase are missing unit tests.
It can be used as a development dependency in your project.

Install it with the following command:

```bash
uv add --dev https://github.com/rterluun/missing-unittests.git
```

You can then run the utility with the following command from the command line in the root of your project:

Show help:

```bash
missing-unittests --help
```

Run the utility to check for missing unit tests:

```bash
missing-unittests --src-folder <path-to-source-folder> --tests-folder <path-to-test-folder> --[no-]fail-on-missing-tests
```

Where the arguments are:

| Argument | Description |
| ---------- | ------------- |
| `--src-folder` | The path to the folder containing your source code. |
| `--tests-folder` | The path to the folder containing your unit tests. |
| `--fail-on-missing-tests` | If this flag is set, the utility will exit with a non-zero status code if any functions are found to be missing unit tests. If this flag is not set, the utility will exit with a zero status code even if there are missing tests. |
| `--no-fail-on-missing-tests` | If this flag is set, the utility will exit with a zero status code even if there are missing tests. |

## Use it as a pre-commit hook

You can also use this utility as a pre-commit hook to ensure that all functions in your codebase have corresponding unit tests before committing your changes.
To set it up add the following to your `.pre-commit-config.yaml` file:

```yaml
-   repo: local
    hooks:
    - id: missing-unittests
      name: Check for missing unit tests
      entry: missing-unittests
      language: python
      pass_filenames: false
      args:
        - --fail-on-missing-tests
```
<!-- markdownlint-restore MD013-->
