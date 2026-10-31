"""
models.py  -  NoSQL CRUD operations (Data Access Layer)
Indie Game: Skill Tree & Quest Dependency Engine

DBMS Assignment - 10 (Mini Project)
Name    : Aditya Yadnik
Class   : SY CS-A
Roll No : 2070134
PRN     : 1251070951

Key NoSQL concepts demonstrated:
  - INSERT  ->  insert_one / insert_many
  - READ    ->  find_one / find (with filters, projections, sort)
  - UPDATE  ->  update_one with $set, $inc, $push operators
  - DELETE  ->  delete_one / delete_many
  - Embedded documents  (inventory, objectives inside a single document)
  - Array fields        ($push to append, $in to match arrays)
  - Aggregation pipeline (group, sum, sort)
"""

from datetime import datetime
from bson import ObjectId
from pymongo.database import Database


# ════════════════════════════════════════════════════════════
#  PLAYERS
# ════════════════════════════════════════════════════════════

def create_player(db: Database, username: str, hero_class: str, bio: str = "") -> str:
    """
    Insert a new player document.
    Notice: the document is a nested dict — no fixed schema required.
    Returns the inserted _id as string.
    """
    doc = {
        "username":   username.strip(),
        "hero_class": hero_class.strip(),
        "bio":        bio.strip(),
        "level":      1,
        "xp":         0,
        "gold":       100,
        "created_at": datetime.utcnow(),
        # Embedded sub-document — NoSQL advantage over relational tables
        "stats": {
            "strength":  10,
            "agility":   10,
            "intellect": 10,
            "endurance": 10,
        },
        # Embedded array of items (would need a separate table in SQL)
        "inventory": [],
        # Array of unlocked skill_codes
        "unlocked_skills": [],
    }
    result = db.players.insert_one(doc)
    return str(result.inserted_id)


def get_all_players(db: Database) -> list:
    # Projection: include only the fields we want to display
    cursor = db.players.find(
        {},
        {"username": 1, "hero_class": 1, "level": 1, "xp": 1, "gold": 1, "created_at": 1}
    ).sort("username", 1)
    return list(cursor)


def find_player(db: Database, username: str):
    """Case-insensitive partial match using a regex query."""
    return db.players.find_one(
        {"username": {"$regex": username, "$options": "i"}}
    )


def get_player_by_id(db: Database, player_id: str):
    return db.players.find_one({"_id": ObjectId(player_id)})


def award_xp(db: Database, player_id: str, xp: int, gold: int = 0) -> bool:
    """
    Use $inc operator to atomically increment XP and gold.
    Also auto-level-up every 500 XP.
    """
    result = db.players.update_one(
        {"_id": ObjectId(player_id)},
        {
            "$inc": {"xp": xp, "gold": gold},
        }
    )
    # Check and apply level-up
    player = db.players.find_one({"_id": ObjectId(player_id)}, {"xp": 1, "level": 1})
    if player:
        new_level = max(1, player["xp"] // 500 + 1)
        if new_level != player["level"]:
            db.players.update_one(
                {"_id": ObjectId(player_id)},
                {"$set": {"level": new_level}}
            )
    return result.modified_count > 0


def unlock_skill_for_player(db: Database, player_id: str, skill_code: str) -> bool:
    """Use $addToSet to add to array only if not already present."""
    result = db.players.update_one(
        {"_id": ObjectId(player_id)},
        {"$addToSet": {"unlocked_skills": skill_code}}
    )
    return result.modified_count > 0


def add_to_inventory(db: Database, player_id: str, item: dict) -> bool:
    """$push appends an embedded item document into the inventory array."""
    item["acquired_at"] = datetime.utcnow()
    result = db.players.update_one(
        {"_id": ObjectId(player_id)},
        {"$push": {"inventory": item}}
    )
    return result.modified_count > 0


def delete_player(db: Database, player_id: str) -> bool:
    result = db.players.delete_one({"_id": ObjectId(player_id)})
    return result.deleted_count > 0


# ════════════════════════════════════════════════════════════
#  SKILLS
# ════════════════════════════════════════════════════════════

def create_skill(db: Database, skill_code: str, name: str, category: str,
                 description: str, xp_cost: int, prerequisites: list) -> str:
    """
    Skill document stores prerequisites as an array of skill_codes.
    This is a graph-edge stored inside the document — no JOIN table needed.
    """
    doc = {
        "skill_code":    skill_code.upper().strip(),
        "name":          name.strip(),
        "category":      category.strip(),
        "description":   description.strip(),
        "xp_cost":       xp_cost,
        "prerequisites": prerequisites,   # e.g. ["BASIC_SWORD", "AGILITY_I"]
        "passive_bonus": {},
        "created_at":    datetime.utcnow(),
    }
    result = db.skills.insert_one(doc)
    return str(result.inserted_id)


def get_all_skills(db: Database) -> list:
    return list(db.skills.find().sort([("category", 1), ("xp_cost", 1)]))


def get_skills_by_category(db: Database, category: str) -> list:
    return list(db.skills.find({"category": {"$regex": category, "$options": "i"}}))


def find_skill(db: Database, skill_code: str):
    return db.skills.find_one({"skill_code": skill_code.upper()})


def get_available_skills(db: Database, unlocked: list) -> list:
    """
    Find skills whose prerequisites are ALL contained in the unlocked list.
    Uses $not + $elemMatch — a query impossible to write simply in SQL.
    """
    return list(db.skills.find({
        "skill_code": {"$nin": unlocked},         # not already unlocked
        "$or": [
            {"prerequisites": {"$size": 0}},      # no prerequisites
            {"prerequisites": {"$not": {"$elemMatch": {"$nin": unlocked}}}}
                                                   # all prereqs met
        ]
    }))


# ════════════════════════════════════════════════════════════
#  QUESTS
# ════════════════════════════════════════════════════════════

def create_quest(db: Database, quest_code: str, title: str, difficulty: str,
                 description: str, objectives: list, rewards: dict,
                 required_skills: list) -> str:
    """
    A quest document embeds its objectives and rewards directly.
    objectives: list of dicts, e.g. [{"task": "Defeat Orc", "count": 5}]
    rewards:    dict,          e.g. {"xp": 300, "gold": 150, "item": "Iron Shield"}
    """
    doc = {
        "quest_code":      quest_code.upper().strip(),
        "title":           title.strip(),
        "difficulty":      difficulty,
        "description":     description.strip(),
        "objectives":      objectives,         # embedded array of sub-docs
        "rewards":         rewards,            # embedded sub-document
        "required_skills": required_skills,
        "created_at":      datetime.utcnow(),
    }
    result = db.quests.insert_one(doc)
    return str(result.inserted_id)


def get_all_quests(db: Database) -> list:
    return list(db.quests.find().sort([("difficulty", 1), ("title", 1)]))


def find_quest(db: Database, quest_code: str):
    return db.quests.find_one({"quest_code": quest_code.upper()})


def get_available_quests(db: Database, unlocked_skills: list) -> list:
    """Quests the player has the required skills for."""
    return list(db.quests.find({
        "$or": [
            {"required_skills": {"$size": 0}},
            {"required_skills": {"$not": {"$elemMatch": {"$nin": unlocked_skills}}}}
        ]
    }).sort("difficulty", 1))


# ════════════════════════════════════════════════════════════
#  PROGRESS TRACKING
# ════════════════════════════════════════════════════════════

def start_quest(db: Database, player_id: str, quest_code: str) -> bool:
    """Upsert a progress document for this player + quest."""
    try:
        db.progress.update_one(
            {"player_id": player_id, "ref_code": quest_code.upper(), "type": "quest"},
            {"$setOnInsert": {
                "player_id":  player_id,
                "ref_code":   quest_code.upper(),
                "type":       "quest",
                "status":     "In Progress",
                "started_at": datetime.utcnow(),
                "completed_at": None,
            }},
            upsert=True
        )
        return True
    except Exception:
        return False


def complete_quest(db: Database, player_id: str, quest_code: str) -> dict | None:
    """
    Mark quest complete, award XP + gold from the quest's embedded rewards doc.
    Returns the rewards dict so the UI can display them.
    """
    quest = find_quest(db, quest_code)
    if not quest:
        return None

    db.progress.update_one(
        {"player_id": player_id, "ref_code": quest_code.upper(), "type": "quest"},
        {"$set": {"status": "Completed", "completed_at": datetime.utcnow()}}
    )
    rewards = quest.get("rewards", {})
    award_xp(db, player_id, rewards.get("xp", 0), rewards.get("gold", 0))
    if rewards.get("item"):
        add_to_inventory(db, player_id,
                         {"name": rewards["item"], "source": f"Quest: {quest['title']}"})
    return rewards


def get_player_progress(db: Database, player_id: str) -> list:
    return list(db.progress.find({"player_id": player_id}).sort("started_at", -1))


# ════════════════════════════════════════════════════════════
#  AGGREGATION (Analytics)
# ════════════════════════════════════════════════════════════

def leaderboard(db: Database, top_n: int = 10) -> list:
    """MongoDB aggregation pipeline: group by nothing, sort by XP."""
    pipeline = [
        {"$project": {"username": 1, "hero_class": 1, "level": 1, "xp": 1, "gold": 1}},
        {"$sort": {"xp": -1}},
        {"$limit": top_n},
    ]
    return list(db.players.aggregate(pipeline))


def skill_category_stats(db: Database) -> list:
    """Aggregation: count skills per category and average XP cost."""
    pipeline = [
        {"$group": {
            "_id":           "$category",
            "total_skills":  {"$sum": 1},
            "avg_xp_cost":   {"$avg": "$xp_cost"},
            "min_xp":        {"$min": "$xp_cost"},
            "max_xp":        {"$max": "$xp_cost"},
        }},
        {"$sort": {"total_skills": -1}},
    ]
    return list(db.skills.aggregate(pipeline))


def quest_completion_stats(db: Database) -> dict:
    """Count completed vs in-progress quests across all players."""
    pipeline = [
        {"$match": {"type": "quest"}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    result = {r["_id"]: r["count"] for r in db.progress.aggregate(pipeline)}
    return result


def get_summary_stats(db: Database) -> dict:
    return {
        "total_players":   db.players.count_documents({}),
        "total_skills":    db.skills.count_documents({}),
        "total_quests":    db.quests.count_documents({}),
        "active_quests":   db.progress.count_documents({"type": "quest", "status": "In Progress"}),
        "completed_quests":db.progress.count_documents({"type": "quest", "status": "Completed"}),
    }

get_summary = get_summary_stats
