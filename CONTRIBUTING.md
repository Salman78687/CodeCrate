# Contributing

Thanks for helping improve CodeCrate.

## Set up

Follow [Development](README.md#development) in the README.

## Making a change

1. Fork the repository and branch from `main`.
2. Keep each pull request to one change.
3. Before opening it, make sure these pass:
   ```bash
   flake8 src tests
   pytest
   cd frontend && CI=true npm run build
   ```
4. Add or update tests for behaviour you change. Executor tests use a fake Docker client (see `tests/test_executor.py`), so they run without Docker.

## Adding a language

1. Add an entry to `LANGUAGES` in `src/codecrate/executor.py`: the image, the file name the code is saved as, and the command that compiles and runs it. Use an official, pinned image tag.
2. Add the language to the lists in `frontend/src/App.js` (name, starter code, Monaco language id).
3. Check that a hello-world runs within the default limits (`CODECRATE_TIMEOUT=15`, `CODECRATE_MEMORY=256m`, `CODECRATE_CPUS=0.5`, `CODECRATE_PIDS_LIMIT=64`), and update the README's language table.

## Security-sensitive changes

Changes to the sandbox settings in `CodeExecutor.run_code` need extra care: never pass user code through the shell command line, and don't loosen the container's limits without explaining why in the pull request. To report a vulnerability, follow [SECURITY.md](SECURITY.md) rather than opening a public issue.
