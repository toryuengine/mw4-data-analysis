"""DB への接続と、武器・アタッチメントの取得。

接続情報はプロジェクト直下の .env から読む（.env.example を参照）。
"""

import os

import mysql.connector
from dotenv import load_dotenv

from brute_force import SLOTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}


def connect():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_weapon(weapon_id):
    """weapon テーブルの 1 行を辞書で返す。なければ ValueError。"""
    conn = connect()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM weapon WHERE id = %s", (weapon_id,))
        weapon = cursor.fetchone()
    finally:
        conn.close()
    if weapon is None:
        raise ValueError(f"武器id {weapon_id} は weapon テーブルにありません")
    return weapon


def fetch_attachments(weapon_id):
    """{スロット名: {ident: アタッチメントの行(辞書)}} を返す。アタッチメントがないスロットは含めない。"""
    conn = connect()
    try:
        cursor = conn.cursor(dictionary=True)
        attachments = {}
        for slot in SLOTS:
            cursor.execute(f"SELECT * FROM `{slot}` WHERE weapon_id = %s ORDER BY ident", (weapon_id,))
            rows = cursor.fetchall()
            if rows:
                attachments[slot] = {r["ident"]: r for r in rows}
        return attachments
    finally:
        conn.close()
