# AGENTS Instructions for NotiPy

These guidelines apply to automated contributions made by language model agents.

## Style and Testing

- Format Python code using `black` if any Python files are modified.
- Always run `pytest -q` after making changes. The repository may not have tests,
  but the command must still be executed and results noted in the PR.

## Documentation

- Documentation resides in `docs/<lang>/` directories. The root `README.md`
  points to these translations.

## Commit and PR Guidelines

- Commit messages should be short and in English.
- The pull request summary must briefly describe what was changed and include
  the output of the test command.
