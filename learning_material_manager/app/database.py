from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import mysql.connector
from dotenv import load_dotenv


# Speichert Projektpfade an einer zentralen Stelle.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


def load_environment() -> None:
    # Laedt Datenbankeinstellungen aus der lokalen .env-Datei.
    load_dotenv(dotenv_path=ENV_FILE)


def get_connection() -> mysql.connector.MySQLConnection:
    # Erstellt eine MySQL-Verbindung mit Werten aus der Umgebung.
    load_environment()
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "learning_material_db"),
    )


def fetch_all(query: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
    # Fuehrt eine SELECT-Abfrage aus und gibt Zeilen als Dictionary zurueck.
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def execute_query(query: str, params: tuple[Any, ...] | None = None) -> int:
    # Fuehrt eine INSERT-Abfrage aus und gibt den neuen Primaerschluessel zurueck.
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params or ())
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()


def execute_change(query: str, params: tuple[Any, ...] | None = None) -> int:
    # Fuehrt eine UPDATE- oder DELETE-Abfrage aus und gibt die Anzahl geaenderter Zeilen zurueck.
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params or ())
        connection.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        connection.close()


def execute_transaction(queries: list[tuple[str, tuple[Any, ...]]]) -> list[int]:
    # Fuehrt mehrere Schreibabfragen als eine Datenbanktransaktion aus.
    connection = get_connection()
    cursor = connection.cursor()
    row_counts: list[int] = []
    try:
        for query, params in queries:
            cursor.execute(query, params)
            row_counts.append(cursor.rowcount)
        connection.commit()
        return row_counts
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
