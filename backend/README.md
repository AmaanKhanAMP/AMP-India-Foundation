# AIF Backend (Flask)

CMS API, MySQL models, and chatbot sync trigger.

**Full project documentation:** [AIF_CHATBOT_DOCUMENTATION.md](../AIF_CHATBOT_DOCUMENTATION.md)

Historical package README: [`docs/archive/backend_README.md`](../docs/archive/backend_README.md)

## Quick start

```bash
python -m venv .venv
# activate venv
pip install -r requirements.txt
# configure .env (DB + CHATBOT_URL + ingest token)
flask db upgrade
python app.py
```

Default port: **5000**.
