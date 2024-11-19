# ${REPO_NAME}

## Direnv

An impure virtual environment (in `.venv`) is handy for using Pycharm in development and for using a system-installed `uv`.

```bash
# .envrc
use flake .#impure
uv sync
```

otherwise you can let `uv2nix` create the virtual environment.

```bash
# .envrc
use flake
```

## Environment Variables

Some sensible default setting for production.

- The PostgresQL database uses the default the Unix socket with peer authentication.
- A connection pool is configured.
- Two `gunicorn` workers are started.

```shell
DJANGO_ALLOWED_HOSTS="${REPO_NAME}.j3ff.io,127.0.0.1"
DJANGO_SECRET_KEY=<REPLACE>
DJANGO_DATABASE_URL=postgres:///${REPO_NAME}
DJANGO_DATABASE_OPTIONS='{"pool": {"min_size": 2, "max_size": 4}}'
WEB_CONCURRENCY=2
```
