# SQLite File Cabinet

A lightweight FastAPI service that stores SQLite database files as opaque files. It never opens a database with SQLite and never executes SQL.

## Important Render storage warning

Render Free web services use an ephemeral filesystem. Files stored under `STORAGE_ROOT` can disappear after a restart or deploy. Use the free tier only for testing. For durable storage, use a paid Render persistent disk or change the service to use external object storage.

## Layout

```text
sqlite_file_cabinet/
├── app/
│   ├── __init__.py
│   └── main.py
├── .gitignore
├── .python-version
├── make_token.py
├── README.md
├── render.yaml
└── requirements.txt
```

## Environment variables

- `APP_TOKEN_SECRET` — required; at least 32 bytes. It signs a separate deterministic token for each `user_id`.
- `STORAGE_ROOT` — file storage directory. Default: `./storage`.
- `MAX_FILE_SIZE_BYTES` — maximum upload size. Default: `1073741824` (1 GiB). Set to `0` for no application-level limit.

Generate a secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Generate a token for user `alice` using the same secret:

Windows PowerShell:

```powershell
$env:APP_TOKEN_SECRET = "paste-the-secret-here"
python make_token.py alice
```

macOS/Linux:

```bash
export APP_TOKEN_SECRET='paste-the-secret-here'
python make_token.py alice
```

## Run locally

```bash
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

## API usage

Uploads are a raw binary request body (`application/octet-stream`), which allows `Request.stream()` to write chunks directly to a temporary file without loading the complete database into RAM.

```bash
# Upload or replace
curl -X POST \
  -H "X-App-Token: YOUR_USER_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @local.db \
  https://YOUR-SERVICE.onrender.com/sync/alice/main

# Download
curl -f \
  -H "X-App-Token: YOUR_USER_TOKEN" \
  -o downloaded.db \
  https://YOUR-SERVICE.onrender.com/fetch/alice/main

# List
curl -H "X-App-Token: YOUR_USER_TOKEN" \
  https://YOUR-SERVICE.onrender.com/list/alice

# Delete
curl -X DELETE \
  -H "X-App-Token: YOUR_USER_TOKEN" \
  https://YOUR-SERVICE.onrender.com/remove/alice/main
```

## Render deployment

1. Push this folder to a GitHub repository.
2. In Render, create a **Blueprint** and select the repository. Render reads `render.yaml`.
3. Enter `APP_TOKEN_SECRET` when prompted. Use the random secret generation command above and save the value securely.
4. Deploy.
5. Generate each user's token locally with `make_token.py` and the exact same secret.

For a paid persistent disk, mount it at `/var/data` and change `STORAGE_ROOT` to `/var/data/sqlite-files`. Keep one Uvicorn worker because a Render persistent disk is attached to one service instance and the service uses process-local per-file locks.
