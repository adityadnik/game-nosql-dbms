# DBMS Assignment - 10 (Mini Project)
## Indie Game: Skill Tree & Quest Dependency Engine

![MIT License](https://img.shields.io/badge/License-MIT-green.svg)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-green)
![Python](https://img.shields.io/badge/Language-Python%203-blue)

| Field | Details |
|-------|---------|
| **Name** | Aditya Yadnik |
| **Class** | SY CS-A |
| **Roll No** | 2070134 |
| **PRN** | 1251070951 |
| **Subject** | Database Management Systems (DBMS) |
| **Language** | Python 3 |
| **Database** | MongoDB (NoSQL — Document Store) |
| **Driver** | pymongo 4.x |

---

## How to Run

```bash
# Step 1 — Start MongoDB server
"C:\Program Files\MongoDB\Server\8.3\bin\mongod.exe" --dbpath C:\data\db

# Step 2 — (In a new terminal) Load sample data
cd game-nosql-dbms
python3 seed_demo.py

# Step 3 — Launch the application
python3 main.py
```

---

## Project Structure

| File | Purpose |
|------|---------|
| `database.py` | MongoDB connection, collection creation, indexes |
| `models.py` | All NoSQL CRUD + aggregation pipeline operations |
| `ui.py` | Terminal UI (colours, tables, prompts) |
| `main.py` | Menu controller / entry point |
| `seed_demo.py` | Loads 5 players, 13 skills, 5 quests, 6 progress records |

---

## Database Schema (Document Structure)

### players collection
```json
{
  "_id": ObjectId,
  "username": "AaravWarrior",
  "hero_class": "Warrior",
  "level": 2, "xp": 650, "gold": 300,
  "stats": { "strength": 10, "agility": 10, "intellect": 10, "endurance": 10 },
  "inventory": [
    { "name": "Iron Sword", "type": "Weapon", "rarity": "Common", "acquired_at": Date }
  ],
  "unlocked_skills": ["BASIC_SWORD", "SHIELD_BASH"]
}
```

### skills collection
```json
{
  "_id": ObjectId,
  "skill_code": "ADV_SWORD",
  "name": "Advanced Sword Combat",
  "category": "Combat",
  "xp_cost": 150,
  "prerequisites": ["BASIC_SWORD"]
}
```

### quests collection
```json
{
  "_id": ObjectId,
  "quest_code": "DRAGON_LAIR",
  "title": "Into the Dragon's Lair",
  "difficulty": "Hard",
  "objectives": [
    { "task": "Defeat Elder Dragon Pyraxis", "count": 1 }
  ],
  "rewards": { "xp": 1000, "gold": 750, "item": "Dragon Scale Armor" },
  "required_skills": ["ADV_SWORD", "FIRE_II"]
}
```

---

## NoSQL Concepts Demonstrated

| Concept | Where Used |
|---------|-----------|
| **MongoDB Connection** | `get_db()` in `database.py` |
| **Collections + Indexes** | `initialise_collections()` — unique & compound indexes |
| **INSERT** | `insert_one()` — players, skills, quests |
| **READ** | `find()`, `find_one()` with filters & projections |
| **UPDATE** | `update_one()` with `$set`, `$inc`, `$push`, `$addToSet` |
| **DELETE** | `delete_one()` — remove player |
| **Embedded Documents** | `stats` and `rewards` nested inside player/quest doc |
| **Embedded Arrays** | `inventory`, `unlocked_skills`, `objectives`, `prerequisites` |
| **Regex Query** | `$regex` for case-insensitive player/skill search |
| **Array Operators** | `$in`, `$nin`, `$elemMatch`, `$size`, `$not` |
| **Upsert** | `update_one(..., upsert=True)` for progress tracking |
| **Aggregation Pipeline** | Leaderboard, skill category stats, quest completion counts |
| **Schema Flexibility** | No fixed columns — documents can have different shapes |

---

## Why NoSQL for a Game Engine?

| Requirement | SQL (Relational) | NoSQL (MongoDB) |
|-------------|-----------------|-----------------|
| Player inventory | Separate `inventory` table + JOIN | Embedded array in player doc |
| Quest objectives | Separate `objectives` table | Embedded array in quest doc |
| Skill prerequisites | Junction table | Array field `prerequisites: []` |
| Flexible player stats | Fixed columns | Any fields, any time |
| Read a full player profile | Multiple JOINs | Single document read |
