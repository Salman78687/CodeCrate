# CodeCrate

Write code in the browser and run it in **Python, JavaScript, Java, C++ or Go**. Each run happens in a fresh, locked-down Docker container that is deleted afterwards.

- **Editor:** Monaco (the editor from VS Code) with syntax highlighting
- **Sandbox:** no network, read-only filesystem, unprivileged user, CPU, memory, process and time limits
- **API:** a small FastAPI service you can call directly, with OpenAPI docs
- **One command to run:** `docker compose up --build`

> **Security first:** CodeCrate runs arbitrary code. Read [Security](#security) before exposing it to anyone you don't trust.

---

## Quick start (Docker)

You need [Docker](https://docs.docker.com/get-docker/) with Docker Compose, on Linux, macOS or Windows (WSL2).

```bash
git clone https://github.com/Salman78687/CodeCrate.git
cd CodeCrate
docker compose up --build -d
```

| What | URL |
|---|---|
| Web app | http://localhost:3000 |
| API docs (Swagger) | http://localhost:8000/api/docs |
| Health check | http://localhost:8000/health |

The first start takes a few minutes: it builds the app and downloads the language images (about 3 GB in total). Runs are fast after that.

Stop it with `docker compose down`.

---

## Supported languages

| Language | `language` id | Image |
|---|---|---|
| Python 3.12 | `python` | `python:3.12-slim` |
| JavaScript (Node.js 22) | `javascript` | `node:22-slim` |
| Java 21 | `java` | `eclipse-temurin:21-jdk` |
| C++ (GCC 14) | `cpp` | `gcc:14` |
| Go 1.23 | `go` | `codecrate-go:1.23` (built from [`sandbox/go`](sandbox/go)) |

Java code must define `public class Main`. Go code must be `package main`.

The Go image is `golang:1.23` plus a pre-compiled standard library. Without it, every Go run would compile the runtime from scratch, which takes 20 to 40 seconds under the sandbox's CPU limit. Docker Compose builds it for you.

To add a language, add an entry to `LANGUAGES` in [`src/codecrate/executor.py`](src/codecrate/executor.py) and to the lists in [`frontend/src/App.js`](frontend/src/App.js).

---

## Using the API

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"language": "python", "code": "print(\"Hello, World!\")"}'
```

```json
{
  "output": "Hello, World!\n",
  "stderr": null,
  "error": null,
  "exitCode": 0,
  "executionTime": 0.12
}
```

- `stderr` holds compiler errors and anything the program writes to standard error.
- `error` is set only when the run couldn't finish normally, for example a timeout (`exitCode` 124) or the memory limit (`exitCode` 137).

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/execute` | Run code |
| `GET /api/v1/languages` | List languages |
| `GET /api/v1/health` (also `/health`) | Is the API up and can it reach Docker? |
| `GET /api/v1/metrics` | Run counts, success rate, average time (in memory, reset on restart) |

---

## Configuration

All settings are optional environment variables on the API. With Docker Compose, set them in your shell or in a `.env` file next to `docker-compose.yml`.

| Variable | Default | Meaning |
|---|---|---|
| `CODECRATE_TIMEOUT` | `15` | Seconds a run may take, including compiling |
| `CODECRATE_MEMORY` | `256m` | Memory per run (no swap) |
| `CODECRATE_CPUS` | `0.5` | CPU cores per run |
| `CODECRATE_PIDS_LIMIT` | `64` | Max processes and threads per run (stops fork bombs) |
| `CODECRATE_TMP_SIZE` | `128m` | Size of the writable `/tmp` in each run |
| `CODECRATE_MAX_CONCURRENT` | `4` | Runs allowed at the same time; extra requests wait |
| `CODECRATE_MAX_CODE_BYTES` | `65536` | Largest accepted program |
| `CODECRATE_MAX_OUTPUT` | `65536` | Output is cut off after this many characters |
| `CODECRATE_PREPULL` | `true` | Download the language images when the API starts |
| `CODECRATE_CORS_ORIGINS` | `http://localhost:3000` | Comma-separated origins allowed to call the API from a browser |

The frontend has one build-time setting, `REACT_APP_API_URL`. Leave it empty (the default) to call the API on the same origin, which is what the Docker setup does via nginx.

---

## Development

Requires Python 3.10+, Node.js 20+ and Docker.

```bash
# Backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
docker build -t codecrate-go:1.23 sandbox/go   # once, for Go support
uvicorn codecrate.main:app --reload            # http://localhost:8000

# Frontend, in a second terminal
cd frontend
npm ci
npm start                                      # http://localhost:3000
```

The dev server proxies API calls to `localhost:8000` (see `proxy` in `frontend/package.json`).

```bash
pytest           # tests use a fake Docker client, so Docker isn't needed
flake8 src tests
```

---

## How it works

```
browser ──▶ nginx (web, :3000) ──/api──▶ FastAPI (api, :8000) ──▶ Docker socket
                                                                    │
                                              one throwaway container per run
```

For each run the API:

1. passes the code to the container as base64 in an environment variable, so it is never spliced into a shell command;
2. starts the language image with the limits above: no network, read-only root filesystem, a small writable `/tmp`, user `nobody`, all Linux capabilities dropped and `no-new-privileges`;
3. waits up to `CODECRATE_TIMEOUT` seconds, then kills it;
4. returns stdout and stderr separately (truncated if huge) and deletes the container.

---

## Security

Running untrusted code is risky, and Docker containers are **not** a perfect security boundary. Understand these points before you deploy CodeCrate:

- **The API controls Docker on its host.** It needs the Docker socket to start containers, and access to that socket is equivalent to root on the host. A bug in the API, or a container escape through a kernel or Docker vulnerability, could compromise the whole machine.
- **There is no authentication or rate limiting.** By default both ports are bound to `127.0.0.1`, so only your machine can reach them. Don't publish them to the internet as-is.
- **If you do host it for others:**
  - Run it on a dedicated, disposable VM with nothing else on it.
  - Put authentication and rate limiting in front of it.
  - Consider a stronger sandbox runtime such as [gVisor](https://gvisor.dev/) (`runsc`) for the code containers.
  - Never expose the Docker daemon over TCP without TLS.

To report a vulnerability, see [SECURITY.md](SECURITY.md).

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
