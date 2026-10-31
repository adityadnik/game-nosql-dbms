# DBMS Assignment - 10 (Mini Project)
## Indie Game: Skill Tree & Quest Dependency Engine — Document-Based NoSQL System

![MIT License](https://img.shields.io/badge/License-MIT-green.svg)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248.svg?logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/Language-Python%203-blue.svg)
![PyMongo](https://img.shields.io/badge/Driver-PyMongo%204.x-brightgreen.svg)

| Field | Details |
|-------|---------|
| **Name** | Aditya Yadnik |
| **Class** | SY CS-A |
| **Roll No** | 2070134 |
| **PRN** | 1251070951 |
| **Subject** | Database Management Systems (DBMS) |
| **Assignment** | Assignment 10: Database Connectivity with Non-Relational (NoSQL) Database |
| **Language** | Python 3 |
| **Database Engine** | MongoDB (Document-Oriented NoSQL) |
| **Python Driver** | `pymongo 4.19.0` |

---

## 📖 What It Is

The **Skill Tree & Quest Dependency Engine** is a NoSQL database application built to power core RPG / indie game backend mechanics. Players explore game worlds, unlock interdependent abilities across branched skill trees, accept dynamic quests with multiple sub-objectives, and receive loot/XP rewards upon completion.

### Why Relational Databases Struggle Here (The NoSQL Value Proposition)
In game development, player state and game design elements evolve continuously:
1. **Polymorphic Player Inventories:** A player's inventory contains weapons, consumable potions, spellbooks, and key items—each with wildly different attributes (durability, attack power, mana cost, potion duration). In traditional SQL, this requires either many empty nullable columns or complex EAV (Entity-Attribute-Value) anti-patterns. In MongoDB, each item is stored naturally as a polymorphic embedded document within the `inventory` array.
2. **Graph-Like Dependency Trees:** Skills depend on multiple parent skills (e.g., `BERSERKER` requires both `ADV_SWORD` and `SHIELD_BASH`). In SQL, traversing prerequisite hierarchies requires recursive CTEs or heavy junction tables. In MongoDB, dependencies are embedded directly as arrays (`prerequisites: ["ADV_SWORD", "SHIELD_BASH"]`) and resolved in a single document query using array operators (`$nin`, `$elemMatch`).
3. **Compound Quest Payloads:** Quests hold variable task lists and dynamic reward packages. Storing objectives and rewards directly inside quest documents eliminates 3-4 table joins per quest evaluation.

---

## ⚙️ How It Works

The engine is engineered around a clean **3-layer document-driven architecture**:

```
┌────────────────────────────────────────────────────────┐
│            Presentation Layer (ui.py, main.py)         │
│  - Colorized Terminal Menus & Live Leaderboard Screens │
│  - Document Pretty-Printer & User Input Handlers       │
└───────────────────────────┬────────────────────────────┘
                            │ Method Invocations
┌───────────────────────────▼────────────────────────────┐
│      NoSQL Data Access Layer / Engine (models.py)      │
│  - Document Aggregation Pipelines ($match, $group)     │
│  - Atomic Field Mutation ($inc, $push, $addToSet)      │
│  - Prerequisite & Availability Graph Evaluators        │
└───────────────────────────┬────────────────────────────┘
                            │ PyMongo BSON Commands
┌───────────────────────────▼────────────────────────────┐
│              MongoDB Engine (database.py)              │
│  - Collections: players, skills, quests, progress      │
│  - Unique & Compound B-Tree Indexes                    │
│  - Native JSON/BSON Document Storage in game_engine_db │
└────────────────────────────────────────────────────────┘
```

### Core Execution Flow & Lifecycle:

1. **Connection & Index Setup (`database.py`):**
   - Initializes a client connection to `mongodb://localhost:27017/`.
   - Executes a health ping on `admin.command('ping')` to ensure daemon availability.
   - Enforces unique indexing on `username`, `skill_code`, and `quest_code`, plus compound indexing on `progress(player_id, ref_code)`.

2. **Skill Tree Evaluation & Dependency Resolution:**
   - To find available skills for a hero, the engine queries the player's `unlocked_skills` array.
   - MongoDB evaluates the query:
     ```json
     {
       "skill_code": { "$nin": unlocked_skills },
       "$or": [
         { "prerequisites": { "$size": 0 } },
         { "prerequisites": { "$not": { "$elemMatch": { "$nin": unlocked_skills } } } }
       ]
     }
     ```
   - Only skills whose entire prerequisites list is satisfied appear as unlockable.
   - Upon unlocking, the skill code is pushed via `$addToSet`, and XP is deducted atomically via `$inc`.

3. **Dynamic Quest Lifecycle & Multi-Reward Payout:**
   - **Start Quest:** A progress record is registered with status `"In Progress"` using `upsert=True`.
   - **Complete Quest:** 
     - Status updates to `"Completed"` with a timestamp.
     - Rewards are parsed from the quest's embedded `rewards` document.
     - XP and gold are incremented on the player document in one operation (`$inc: { xp: rewards.xp, gold: rewards.gold }`).
     - Level-up calculation is evaluated automatically.
     - If the reward includes a rare item, it is appended to the player's embedded inventory array using `$push`.

4. **Analytics & Aggregation Pipelines:**
   - **Leaderboard:** Streams players, sorts descending by XP (`$sort: { xp: -1 }`), and projects top rankings without manual sorting loops.
   - **Skill Tree Metrics:** Groups skills by category (`$group: { _id: "$category", count: { $sum: 1 }, avg_cost: { $avg: "$xp_cost" } }`).
   - **Quest Completion Ratios:** Aggregates overall active vs completed quest tallies across all users.

---

## 🗄️ MongoDB Document Schemas

### 1. `players` Collection
```json
{
  "_id": ObjectId("6723b7e..."),
  "username": "AaravWarrior",
  "hero_class": "Warrior",
  "bio": "Veteran soldier from the Eastern Plains.",
  "level": 2,
  "xp": 850,
  "gold": 480,
  "created_at": ISODate("2026-10-31T15:53:34.000Z"),
  "stats": {
    "strength": 10,
    "agility": 10,
    "intellect": 10,
    "endurance": 10
  },
  "inventory": [
    {
      "name": "Iron Sword",
      "type": "Weapon",
      "rarity": "Common",
      "acquired_at": ISODate("2026-10-31T15:53:34.000Z")
    }
  ],
  "unlocked_skills": ["BASIC_SWORD", "SHIELD_BASH"]
}
```

### 2. `skills` Collection
```json
{
  "_id": ObjectId("6723b7e..."),
  "skill_code": "BERSERKER",
  "name": "Berserker Rage",
  "category": "Combat",
  "description": "Enter a damage-boosted frenzy mode.",
  "xp_cost": 300,
  "prerequisites": ["ADV_SWORD", "SHIELD_BASH"],
  "created_at": ISODate("2026-10-31T15:53:34.000Z")
}
```

### 3. `quests` Collection
```json
{
  "_id": ObjectId("6723b7e..."),
  "quest_code": "DRAGON_LAIR",
  "title": "Into the Dragon's Lair",
  "difficulty": "Hard",
  "description": "Brave the volcanic mountains and slay the elder dragon Pyraxis.",
  "objectives": [
    { "task": "Survive Dragon Ambush", "count": 1 },
    { "task": "Destroy Dragon Eggs", "count": 5 },
    { "task": "Defeat Elder Dragon Pyraxis", "count": 1 }
  ],
  "rewards": {
    "xp": 1000,
    "gold": 750,
    "item": "Dragon Scale Armor"
  },
  "required_skills": ["ADV_SWORD", "FIRE_II"],
  "created_at": ISODate("2026-10-31T15:53:34.000Z")
}
```

### 4. `progress` Collection
```json
{
  "_id": ObjectId("6723b7e..."),
  "player_id": "6723b7e...",
  "ref_code": "GOBLIN_CAMP",
  "type": "quest",
  "status": "Completed",
  "started_at": ISODate("2026-10-31T15:53:34.000Z"),
  "completed_at": ISODate("2026-10-31T15:53:34.000Z")
}
```

---

## 🚀 How to Run

### Prerequisites
1. **Python 3.8+**
2. **MongoDB Community Server** (installed at `C:\Program Files\MongoDB\Server\8.3\bin\` or added to PATH)
3. **PyMongo Driver**:
   ```bash
   python3 -m pip install pymongo
   ```

### Execution Steps
```bash
# 1. Start MongoDB local server instance (Terminal 1)
"C:\Program Files\MongoDB\Server\8.3\bin\mongod.exe" --dbpath C:\data\db

# 2. In a separate terminal, navigate to the project directory
cd game-nosql-dbms

# 3. Seed demo players, skill trees, quests, and progress records
python3 seed_demo.py

# 4. Launch the application
python3 main.py
```

### Running Automated Test Suite
```bash
python3 test_queries.py
```

---

## 📂 Project Structure

| File | Purpose |
|------|---------|
| `database.py` | MongoDB client connection manager, collection initialization, index builders |
| `models.py` | Data Access Layer: CRUD routines, update operators, aggregation pipelines |
| `ui.py` | ANSI-based terminal user interface, document inspector, tables, prompts |
| `main.py` | Main application controller and interactive navigation router |
| `seed_demo.py` | Comprehensive test data seeder (heroes, abilities, multi-stage quests) |
| `test_queries.py` | Autonomous verification script asserting queries and aggregations |
| `LICENSE` | MIT Open-Source License |

---

## 🎓 NoSQL Concepts Demonstrated

- **BSON / Document Modeling:** Schema-flexible, nested JSON-like records.
- **Embedded Documents vs Normalization:** Embedding player stats and quest rewards directly to achieve high-performance single-read operations without multi-table SQL joins.
- **Embedded Arrays & Array Operations:** Using `$push` for inventories and `$addToSet` for unique skill unlocks.
- **Advanced Query Operators:** Using `$nin`, `$elemMatch`, `$size`, and `$regex` for graph-like prerequisite checking and fuzzy searching.
- **Atomic Field Updates:** Employing `$inc` for XP/gold calculation and `$set` for profile modifications without race conditions.
- **Upsert Patterns:** `update_one(..., upsert=True)` for idempotently tracking quest workflows.
- **Aggregation Framework:** Complex multi-stage aggregation pipelines (`$match`, `$group`, `$sort`, `$limit`, `$project`) computing leaderboards and category metrics.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE) - Copyright (c) 2026 Aditya Yadnik.
