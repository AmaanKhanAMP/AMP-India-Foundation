# AMP India Foundation — Flask Backend

## Setup

1. Create and activate a virtual environment:

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure MySQL credentials in `.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=aif_cms
DB_USER=root
DB_PASSWORD=YOUR_PASSWORD
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

4. Create the MySQL database (once):

```sql
CREATE DATABASE aif_cms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. Run migrations:

```bash
flask --app app.py db init
flask --app app.py db migrate -m "create contact_messages"
flask --app app.py db upgrade
```

6. Start the API:

```bash
python app.py
```

API base URL: `http://localhost:5000`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | DB health check |
| POST | `/api/contact` | Submit contact form |
| GET | `/api/contact/messages` | List contact messages |

## Frontend

Next.js reads `NEXT_PUBLIC_API_URL` (see `frontend/.env.local`).
Contact form posts to `${NEXT_PUBLIC_API_URL}/api/contact`.
