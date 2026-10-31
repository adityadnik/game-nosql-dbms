"""
seed_demo.py  -  Populates MongoDB with sample game data for demonstration.

DBMS Assignment - 10 (Mini Project)
Name    : Aditya Yadnik
Class   : SY CS-A
Roll No : 2070134
PRN     : 1251070951

Run ONCE before the demo:  python3 seed_demo.py
"""

from database import get_db, initialise_collections
import models


def seed():
    db = get_db()
    initialise_collections(db)

    # ── Clear old demo data ───────────────────────────────────────────────────
    db.players.delete_many({})
    db.skills.delete_many({})
    db.quests.delete_many({})
    db.progress.delete_many({})
    print("[SEED] Cleared old data.\n")

    # ── Skills (Skill Tree) ───────────────────────────────────────────────────
    # Each skill stores its prerequisites as an embedded array -
    # no junction table needed (NoSQL advantage)
    skills = [
        # Combat tree
        ("BASIC_SWORD",   "Basic Sword Combat",   "Combat",    "Learn basic sword techniques.",           50,  []),
        ("ADV_SWORD",     "Advanced Sword Combat","Combat",    "Master parry, riposte, and combos.",      150, ["BASIC_SWORD"]),
        ("SHIELD_BASH",   "Shield Bash",          "Combat",    "Stun enemies with a powerful bash.",      100, ["BASIC_SWORD"]),
        ("BERSERKER",     "Berserker Rage",        "Combat",    "Enter a damage-boosted frenzy mode.",     300, ["ADV_SWORD", "SHIELD_BASH"]),
        # Magic tree
        ("FIRE_I",        "Fire Bolt I",           "Magic",     "Hurl a basic fireball at enemies.",       80,  []),
        ("FIRE_II",       "Fire Blast II",         "Magic",     "Supercharged fire explosion.",            200, ["FIRE_I"]),
        ("ICE_I",         "Frost Nova I",          "Magic",     "Freeze nearby enemies briefly.",          80,  []),
        ("ARCANE_MASTERY","Arcane Mastery",        "Magic",     "Boost all spell damage by 30%.",          400, ["FIRE_II", "ICE_I"]),
        # Stealth tree
        ("SNEAK",         "Sneak",                 "Stealth",   "Move silently, reduce detection range.",  60,  []),
        ("BACKSTAB",      "Backstab",              "Stealth",   "Critical hit from behind.",               120, ["SNEAK"]),
        ("SHADOW_STEP",   "Shadow Step",           "Stealth",   "Teleport to a target's shadow.",          250, ["BACKSTAB"]),
        # Survival
        ("HERBALISM",     "Herbalism",             "Survival",  "Identify and harvest medicinal herbs.",   40,  []),
        ("FIRST_AID",     "First Aid",             "Survival",  "Bandage wounds without potions.",         70,  ["HERBALISM"]),
    ]
    for code, name, cat, desc, cost, prereqs in skills:
        sid = models.create_skill(db, code, name, cat, desc, cost, prereqs)
        print(f"  Skill: {name:30}  prereqs: {prereqs or 'None'}")

    # ── Players ───────────────────────────────────────────────────────────────
    # Documents have embedded stats + inventory + unlocked_skills arrays
    players_data = [
        ("AaravWarrior",  "Warrior",   "Veteran soldier from the Eastern Plains."),
        ("PriyaMage",     "Mage",      "Apprentice of the Grand Arcane Academy."),
        ("RahulRogue",    "Rogue",     "Former thief turned bounty hunter."),
        ("SnehaRanger",   "Ranger",    "Guardian of the Silverwood Forest."),
        ("DevPaladin",    "Paladin",   "Holy knight sworn to protect the weak."),
    ]
    player_ids = {}
    for username, hero_class, bio in players_data:
        pid = models.create_player(db, username, hero_class, bio)
        player_ids[username] = pid
        print(f"  Player: {username:20} ({hero_class})")

    # Award XP and unlock some skills
    models.award_xp(db, player_ids["AaravWarrior"], 650, 300)
    models.unlock_skill_for_player(db, player_ids["AaravWarrior"], "BASIC_SWORD")
    models.unlock_skill_for_player(db, player_ids["AaravWarrior"], "SHIELD_BASH")
    models.add_to_inventory(db, player_ids["AaravWarrior"],
                            {"name": "Iron Sword", "type": "Weapon", "rarity": "Common"})

    models.award_xp(db, player_ids["PriyaMage"], 820, 500)
    models.unlock_skill_for_player(db, player_ids["PriyaMage"], "FIRE_I")
    models.unlock_skill_for_player(db, player_ids["PriyaMage"], "FIRE_II")
    models.unlock_skill_for_player(db, player_ids["PriyaMage"], "ICE_I")
    models.add_to_inventory(db, player_ids["PriyaMage"],
                            {"name": "Staff of Flames", "type": "Weapon", "rarity": "Rare"})

    models.award_xp(db, player_ids["RahulRogue"], 400, 250)
    models.unlock_skill_for_player(db, player_ids["RahulRogue"], "SNEAK")
    models.unlock_skill_for_player(db, player_ids["RahulRogue"], "BACKSTAB")

    models.award_xp(db, player_ids["SnehaRanger"], 200, 150)
    models.unlock_skill_for_player(db, player_ids["SnehaRanger"], "HERBALISM")

    models.award_xp(db, player_ids["DevPaladin"], 550, 400)
    models.unlock_skill_for_player(db, player_ids["DevPaladin"], "BASIC_SWORD")
    models.add_to_inventory(db, player_ids["DevPaladin"],
                            {"name": "Holy Shield", "type": "Armor", "rarity": "Epic"})

    # ── Quests ────────────────────────────────────────────────────────────────
    # Each quest document embeds objectives AND rewards - no extra tables needed
    quests = [
        (
            "GOBLIN_CAMP", "Goblin Camp Raid", "Easy",
            "Clear the goblin infestation near Millhaven village.",
            [{"task": "Defeat Goblin Scouts",  "count": 10},
             {"task": "Destroy Goblin Totem",  "count": 1}],
            {"xp": 200, "gold": 80,  "item": "Goblin Ear Necklace"},
            []
        ),
        (
            "ANCIENT_RUINS", "Secrets of the Ancient Ruins", "Medium",
            "Explore the crumbling ruins and retrieve the lost artifact.",
            [{"task": "Explore 3 Ruins Chambers", "count": 3},
             {"task": "Defeat Stone Guardian",     "count": 1},
             {"task": "Retrieve the Sundial",      "count": 1}],
            {"xp": 400, "gold": 200, "item": "Ancient Sundial"},
            ["BASIC_SWORD"]
        ),
        (
            "DRAGON_LAIR", "Into the Dragon's Lair", "Hard",
            "Brave the volcanic mountains and slay the elder dragon Pyraxis.",
            [{"task": "Survive Dragon Ambush",   "count": 1},
             {"task": "Destroy Dragon Eggs",      "count": 5},
             {"task": "Defeat Elder Dragon Pyraxis", "count": 1}],
            {"xp": 1000, "gold": 750, "item": "Dragon Scale Armor"},
            ["ADV_SWORD", "FIRE_II"]
        ),
        (
            "SHADOW_GUILD", "Infiltrate the Shadow Guild", "Medium",
            "Sneak into the Shadow Guild headquarters and steal their cipher.",
            [{"task": "Bypass 3 Guard Patrols",   "count": 3},
             {"task": "Pickpocket the Guild Master","count": 1}],
            {"xp": 350, "gold": 300, "item": "Shadow Cipher"},
            ["SNEAK", "BACKSTAB"]
        ),
        (
            "HEALING_HERBS", "The Plague Cure", "Easy",
            "Collect rare healing herbs for the village healer.",
            [{"task": "Collect Moonbloom Herb",  "count": 5},
             {"task": "Collect Sunroot",         "count": 3}],
            {"xp": 150, "gold": 60},
            ["HERBALISM"]
        ),
    ]
    for args in quests:
        qid = models.create_quest(db, *args)
        print(f"  Quest: {args[1]:35}  difficulty: {args[2]}")

    # ── Progress ──────────────────────────────────────────────────────────────
    models.start_quest(db, player_ids["AaravWarrior"], "GOBLIN_CAMP")
    models.complete_quest(db, player_ids["AaravWarrior"], "GOBLIN_CAMP")
    models.start_quest(db, player_ids["AaravWarrior"], "ANCIENT_RUINS")

    models.start_quest(db, player_ids["PriyaMage"], "GOBLIN_CAMP")
    models.complete_quest(db, player_ids["PriyaMage"], "GOBLIN_CAMP")
    models.start_quest(db, player_ids["PriyaMage"], "DRAGON_LAIR")

    models.start_quest(db, player_ids["RahulRogue"], "SHADOW_GUILD")

    models.start_quest(db, player_ids["SnehaRanger"], "HEALING_HERBS")
    models.complete_quest(db, player_ids["SnehaRanger"], "HEALING_HERBS")

    print("\n[OK] Sample data loaded into MongoDB successfully!")
    print("     Run  python3 main.py  to start the application.\n")


if __name__ == "__main__":
    seed()
