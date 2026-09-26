"""Create the MySQL database from .env settings (no password probing)."""

from dotenv import load_dotenv
import os
import sys

import pymysql


def main():
    load_dotenv()
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "3306"))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "aif_cms")

    if not password or password == "YOUR_PASSWORD":
        print(
            "ERROR: Set a real DB_PASSWORD in backend/.env before running this script."
        )
        sys.exit(1)

    try:
        conn = pymysql.connect(host=host, user=user, password=password, port=port)
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        conn.close()
        print(f"Database `{db_name}` is ready.")
    except Exception as exc:
        print(f"Failed to create database: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
