"""
database.py  -  MongoDB connection module
Indie Game: Skill Tree & Quest Dependency Engine

DBMS Assignment - 10 (Mini Project)
Name    : Aditya Yadnik
Class   : SY CS-A
Roll No : 2070134
PRN     : 1251070951

Demonstrates:
  - Connecting to a MongoDB (NoSQL) database using pymongo
  - Creating collections (equivalent of tables, but schema-less)
  - Using indexes for fast lookups
  - Document-oriented storage (nested JSON-like documents)
"""

from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# ── Configuration ─────────────────────────────────────────────────────────────
MONGO_URI  = "mongodb://localhost:27017/"
DB_NAME    = "game_engine_db"

# MongoDB server binary path (used in README / startup hint)
MONGOD_PATH = r"C:\Program Files\MongoDB\Server\8.3\bin\mongod.exe"


def get_db():
    """
    Connect to the local MongoDB server and return the database object.
    Raises a clear error if the server is not running.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        # Trigger connection check
        client.admin.command("ping")
        db = client[DB_NAME]
        return db
    except (ConnectionFailure, ServerSelectionTimeoutError):
        print("\n[ERROR] Cannot connect to MongoDB!")
        print(f"  Start the server with:\n  \"{MONGOD_PATH}\" --dbpath C:\\data\\db\n")
        raise


def initialise_collections(db) -> None:
    """
    Create collections and indexes if they don't already exist.

    Collections (NoSQL equivalent of tables):
      players   - player profiles with embedded inventory & stats
      skills    - skill tree nodes (with prerequisite references)
      quests    - quest documents with embedded objectives & rewards
      progress  - player <-> quest/skill progress tracking
    """

    # ── Players ───────────────────────────────────────────────────────────────
    # Unique index on username
    db.players.create_index([("username", ASCENDING)], unique=True)

    # ── Skills ────────────────────────────────────────────────────────────────
    # Unique index on skill_code; index on category for fast filtering
    db.skills.create_index([("skill_code", ASCENDING)], unique=True)
    db.skills.create_index([("category", ASCENDING)])

    # ── Quests ────────────────────────────────────────────────────────────────
    db.quests.create_index([("quest_code", ASCENDING)], unique=True)
    db.quests.create_index([("difficulty", ASCENDING)])

    # ── Progress ──────────────────────────────────────────────────────────────
    # Compound index: one progress doc per (player, quest/skill)
    db.progress.create_index(
        [("player_id", ASCENDING), ("ref_code", ASCENDING)], unique=True
    )

    print(f"[DB] Connected to MongoDB  ->  database: '{DB_NAME}'")
    print(f"[DB] Collections ready: players, skills, quests, progress\n")
