"""
main.py  -  Entry point & menu controller
Indie Game: Skill Tree & Quest Dependency Engine

DBMS Assignment - 10 (Mini Project)
Name    : Aditya Yadnik
Class   : SY CS-A
Roll No : 2070134
PRN     : 1251070951

Run:  python3 main.py
      (MongoDB must be running: mongod --dbpath C:\data\db)
"""

import sys
import ui
from ui import C
import models
from database import get_db, initialise_collections

ASSIGNMENT   = "DBMS Assignment - 10 (Mini Project)"
APP_TITLE    = "Indie Game: Skill Tree & Quest Dependency Engine"
APP_SUBTITLE = "Python + MongoDB (NoSQL)"
STUDENT_INFO = "Name: Aditya Yadnik  |  Class: SY CS-A  |  Roll No: 2070134  |  PRN: 1251070951"

db = None   # global DB handle, set in main()


# ════════════════════════════════════════════════════════════
#  PLAYERS MENU
# ════════════════════════════════════════════════════════════

def menu_players():
    while True:
        ui.banner(APP_TITLE, "Players", assignment=ASSIGNMENT, student=STUDENT_INFO)
        ui.section("Players Menu")
        choice = ui.prompt_choice([
            "Create New Player",
            "View All Players",
            "View Player Profile (full document)",
            "Search Player by Username",
            "Award XP & Gold",
            "Add Item to Inventory",
            "View Player Quest Progress",
            "Delete Player",
            "<- Back to Main Menu",
        ])
        if choice == 1:   _create_player()
        elif choice == 2: _view_players()
        elif choice == 3: _view_profile()
        elif choice == 4: _search_player()
        elif choice == 5: _award_xp()
        elif choice == 6: _add_inventory()
        elif choice == 7: _player_progress()
        elif choice == 8: _delete_player()
        else: break


def _create_player():
    ui.section("Create New Player")
    username = ui.prompt("Username")
    if not username:
        ui.error("Username cannot be empty."); ui.pause(); return
    classes = ["Warrior", "Mage", "Rogue", "Ranger", "Paladin"]
    ui.info("Choose Hero Class:")
    c = ui.prompt_choice(classes)
    hero_class = classes[c - 1]
    bio = ui.prompt("Bio / backstory (optional)")
    try:
        pid = models.create_player(db, username, hero_class, bio)
        ui.success(f"Player '{username}' created!  ID: {pid}")
        ui.info("Starting stats: STR 10  AGI 10  INT 10  END 10  |  Gold: 100  |  Level: 1")
    except Exception as e:
        ui.error(f"Could not create player: {e}")
    ui.pause()


def _view_players():
    ui.section("All Players")
    players = models.get_all_players(db)
    rows = [
        [str(p["_id"])[-8:], p["username"], p["hero_class"],
         p["level"], p["xp"], p["gold"],
         p["created_at"].strftime("%Y-%m-%d") if p.get("created_at") else "-"]
        for p in players
    ]
    ui.table(rows, ["ID (tail)", "Username", "Class", "Lvl", "XP", "Gold", "Joined"],
             [10, 20, 10, 4, 6, 6, 12])
    ui.pause()


def _view_profile():
    ui.section("Player Full Profile")
    username = ui.prompt("Username")
    p = models.find_player(db, username)
    if not p:
        ui.error("Player not found."); ui.pause(); return
    ui.show_document(p, f"Profile: {p['username']}")
    ui.pause()


def _search_player():
    ui.section("Search Player")
    username = ui.prompt("Username (partial)")
    p = models.find_player(db, username)
    if p:
        ui.show_document(p, f"Found: {p['username']}")
    else:
        ui.warn("No player found.")
    ui.pause()


def _award_xp():
    ui.section("Award XP & Gold")
    username = ui.prompt("Username")
    p = models.find_player(db, username)
    if not p:
        ui.error("Player not found."); ui.pause(); return
    xp   = ui.prompt_int("XP to award", 100)
    gold = ui.prompt_int("Gold to award", 50)
    if models.award_xp(db, str(p["_id"]), xp, gold):
        updated = models.get_player_by_id(db, str(p["_id"]))
        ui.success(f"Awarded {xp} XP + {gold} Gold  |  New total: {updated['xp']} XP, {updated['gold']} Gold, Level {updated['level']}")
    else:
        ui.error("Update failed.")
    ui.pause()


def _add_inventory():
    ui.section("Add Item to Inventory")
    username = ui.prompt("Username")
    p = models.find_player(db, username)
    if not p:
        ui.error("Player not found."); ui.pause(); return
    item_name = ui.prompt("Item name")
    item_type = ui.prompt("Type (Weapon/Armor/Consumable/Quest Item)", "Weapon")
    rarity    = ui.prompt("Rarity (Common/Rare/Epic/Legendary)", "Common")
    item = {"name": item_name, "type": item_type, "rarity": rarity}
    if models.add_to_inventory(db, str(p["_id"]), item):
        ui.success(f"'{item_name}' added to {p['username']}'s inventory.")
    else:
        ui.error("Failed to add item.")
    ui.pause()


def _player_progress():
    ui.section("Player Quest Progress")
    username = ui.prompt("Username")
    p = models.find_player(db, username)
    if not p:
        ui.error("Player not found."); ui.pause(); return
    progress = models.get_player_progress(db, str(p["_id"]))
    if not progress:
        ui.warn("No quest progress found for this player.")
    else:
        rows = [
            [pr["ref_code"], pr["type"].capitalize(),
             pr["status"],
             pr["started_at"].strftime("%Y-%m-%d") if pr.get("started_at") else "-",
             pr["completed_at"].strftime("%Y-%m-%d") if pr.get("completed_at") else "-"]
            for pr in progress
        ]
        ui.table(rows, ["Quest Code", "Type", "Status", "Started", "Completed"],
                 [14, 8, 14, 12, 12])
    ui.pause()


def _delete_player():
    ui.section("Delete Player")
    username = ui.prompt("Username")
    p = models.find_player(db, username)
    if not p:
        ui.error("Player not found."); ui.pause(); return
    confirm = ui.prompt(f"Delete '{p['username']}' permanently? (yes/no)", "no")
    if confirm.lower() == "yes":
        if models.delete_player(db, str(p["_id"])):
            ui.success("Player deleted.")
        else:
            ui.error("Delete failed.")
    else:
        ui.warn("Cancelled.")
    ui.pause()


# ════════════════════════════════════════════════════════════
#  SKILLS MENU
# ════════════════════════════════════════════════════════════

def menu_skills():
    while True:
        ui.banner(APP_TITLE, "Skill Tree", assignment=ASSIGNMENT, student=STUDENT_INFO)
        ui.section("Skill Tree Menu")
        choice = ui.prompt_choice([
            "Add New Skill",
            "View All Skills",
            "View Skills by Category",
            "View Skill Details",
            "Unlock Skill for Player",
            "Show Available Skills for Player",
            "Skill Category Analytics",
            "<- Back to Main Menu",
        ])
        if choice == 1:   _add_skill()
        elif choice == 2: _view_all_skills()
        elif choice == 3: _skills_by_category()
        elif choice == 4: _skill_details()
        elif choice == 5: _unlock_skill()
        elif choice == 6: _available_skills()
        elif choice == 7: _skill_analytics()
        else: break


def _add_skill():
    ui.section("Add New Skill")
    skill_code = ui.prompt("Skill code (e.g. FIRE_BLAST)")
    name       = ui.prompt("Skill name")
    if not skill_code or not name:
        ui.error("Code and name are required."); ui.pause(); return
    categories = ["Combat", "Magic", "Stealth", "Survival", "Leadership", "Crafting"]
    ui.info("Select category:")
    cat = ui.prompt_choice(categories)
    category  = categories[cat - 1]
    desc      = ui.prompt("Description")
    xp_cost   = ui.prompt_int("XP cost to unlock", 100)
    prereqs   = ui.prompt_list("Prerequisites (skill codes)")
    try:
        sid = models.create_skill(db, skill_code, name, category, desc, xp_cost, prereqs)
        ui.success(f"Skill '{name}' added!  Prerequisites: {prereqs or 'None'}")
    except Exception as e:
        ui.error(f"Could not add skill: {e}")
    ui.pause()


def _view_all_skills():
    ui.section("All Skills")
    skills = models.get_all_skills(db)
    rows = [
        [s["skill_code"], s["name"], s["category"], s["xp_cost"],
         ", ".join(s["prerequisites"]) or "None"]
        for s in skills
    ]
    ui.table(rows, ["Code", "Name", "Category", "XP Cost", "Prerequisites"],
             [16, 22, 12, 8, 28])
    ui.pause()


def _skills_by_category():
    ui.section("Skills by Category")
    cat = ui.prompt("Category name (partial)")
    skills = models.get_skills_by_category(db, cat)
    rows = [[s["skill_code"], s["name"], s["xp_cost"],
             ", ".join(s["prerequisites"]) or "None"] for s in skills]
    ui.table(rows, ["Code", "Name", "XP Cost", "Prerequisites"], [16, 24, 8, 30])
    ui.pause()


def _skill_details():
    ui.section("Skill Details")
    code = ui.prompt("Skill code")
    s = models.find_skill(db, code)
    if not s:
        ui.error("Skill not found."); ui.pause(); return
    ui.show_document(s, f"Skill: {s['name']}")
    ui.pause()


def _unlock_skill():
    ui.section("Unlock Skill for Player")
    username = ui.prompt("Username")
    p = models.find_player(db, username)
    if not p:
        ui.error("Player not found."); ui.pause(); return

    code = ui.prompt("Skill code to unlock")
    skill = models.find_skill(db, code)
    if not skill:
        ui.error("Skill not found."); ui.pause(); return

    # Check prerequisites
    unlocked = p.get("unlocked_skills", [])
    missing = [pr for pr in skill["prerequisites"] if pr not in unlocked]
    if missing:
        ui.error(f"Prerequisites not met: {', '.join(missing)}")
        ui.pause(); return

    # Check XP
    if p["xp"] < skill["xp_cost"]:
        ui.error(f"Not enough XP. Need {skill['xp_cost']}, have {p['xp']}.")
        ui.pause(); return

    models.unlock_skill_for_player(db, str(p["_id"]), skill["skill_code"])
    models.award_xp(db, str(p["_id"]), -skill["xp_cost"])  # deduct XP
    ui.success(f"Skill '{skill['name']}' unlocked for {p['username']}! ({skill['xp_cost']} XP spent)")
    ui.pause()


def _available_skills(p=None):
    ui.section("Available Skills for Player")
    if not p:
        username = ui.prompt("Username")
        p = models.find_player(db, username)
        if not p:
            ui.error("Player not found."); ui.pause(); return
    unlocked = p.get("unlocked_skills", [])
    available = models.get_available_skills(db, unlocked)
    ui.info(f"Already unlocked: {', '.join(unlocked) or 'None'}")
    print()
    rows = [[s["skill_code"], s["name"], s["category"], s["xp_cost"],
             ", ".join(s["prerequisites"]) or "None"] for s in available]
    ui.table(rows, ["Code", "Name", "Category", "XP Cost", "Prerequisites"],
             [16, 22, 12, 8, 28])
    ui.pause()


def _skill_analytics():
    ui.section("Skill Category Analytics (Aggregation Pipeline)")
    stats = models.skill_category_stats(db)
    rows = [
        [s["_id"], s["total_skills"], int(s["avg_xp_cost"]), s["min_xp"], s["max_xp"]]
        for s in stats
    ]
    ui.table(rows, ["Category", "# Skills", "Avg XP Cost", "Min XP", "Max XP"],
             [14, 8, 12, 8, 8])
    ui.pause()


# ════════════════════════════════════════════════════════════
#  QUESTS MENU
# ════════════════════════════════════════════════════════════

def menu_quests():
    while True:
        ui.banner(APP_TITLE, "Quests", assignment=ASSIGNMENT, student=STUDENT_INFO)
        ui.section("Quests Menu")
        choice = ui.prompt_choice([
            "Create New Quest",
            "View All Quests",
            "View Quest Details (embedded objectives & rewards)",
            "Start Quest for Player",
            "Complete Quest for Player",
            "View Available Quests for Player",
            "<- Back to Main Menu",
        ])
        if choice == 1:   _create_quest()
        elif choice == 2: _view_quests()
        elif choice == 3: _quest_details()
        elif choice == 4: _start_quest()
        elif choice == 5: _complete_quest()
        elif choice == 6: _available_quests()
        else: break


def _create_quest():
    ui.section("Create New Quest")
    quest_code = ui.prompt("Quest code (e.g. DRAGON_SLAYER)")
    title      = ui.prompt("Quest title")
    if not quest_code or not title:
        ui.error("Code and title required."); ui.pause(); return
    difficulties = ["Easy", "Medium", "Hard", "Legendary"]
    ui.info("Select difficulty:")
    d = ui.prompt_choice(difficulties)
    difficulty = difficulties[d - 1]
    desc = ui.prompt("Description")

    # Embedded objectives
    objectives = []
    ui.info("Add objectives (press Enter with blank task to stop):")
    while True:
        task = ui.prompt("  Objective task (or blank to finish)")
        if not task:
            break
        count = ui.prompt_int("  Required count", 1)
        objectives.append({"task": task, "count": count})

    # Embedded rewards
    xp_reward   = ui.prompt_int("Reward XP",   200)
    gold_reward = ui.prompt_int("Reward Gold",  100)
    item_reward = ui.prompt("Reward Item (optional)")

    rewards = {"xp": xp_reward, "gold": gold_reward}
    if item_reward:
        rewards["item"] = item_reward

    required_skills = ui.prompt_list("Required skills (skill codes)")

    try:
        qid = models.create_quest(db, quest_code, title, difficulty, desc,
                                  objectives, rewards, required_skills)
        ui.success(f"Quest '{title}' created with {len(objectives)} objective(s)!")
    except Exception as e:
        ui.error(f"Could not create quest: {e}")
    ui.pause()


def _view_quests():
    ui.section("All Quests")
    quests = models.get_all_quests(db)
    rows = [
        [q["quest_code"], q["title"], q["difficulty"],
         len(q.get("objectives", [])),
         f"XP:{q['rewards'].get('xp',0)} G:{q['rewards'].get('gold',0)}",
         ", ".join(q.get("required_skills", [])) or "None"]
        for q in quests
    ]
    ui.table(rows, ["Code", "Title", "Difficulty", "Obj#", "Rewards", "Req. Skills"],
             [18, 26, 10, 4, 14, 24])
    ui.pause()


def _quest_details():
    ui.section("Quest Details")
    code = ui.prompt("Quest code")
    q = models.find_quest(db, code)
    if not q:
        ui.error("Quest not found."); ui.pause(); return
    ui.show_document(q, f"Quest: {q['title']}")
    ui.pause()


def _start_quest():
    ui.section("Start Quest")
    username = ui.prompt("Username")
    p = models.find_player(db, username)
    if not p:
        ui.error("Player not found."); ui.pause(); return
    code = ui.prompt("Quest code")
    q = models.find_quest(db, code)
    if not q:
        ui.error("Quest not found."); ui.pause(); return
    # Check required skills
    unlocked = p.get("unlocked_skills", [])
    missing  = [s for s in q.get("required_skills", []) if s not in unlocked]
    if missing:
        ui.error(f"Required skills not unlocked: {', '.join(missing)}")
        ui.pause(); return
    if models.start_quest(db, str(p["_id"]), code):
        ui.success(f"Quest '{q['title']}' started for {p['username']}!")
    else:
        ui.warn("Already started or error.")
    ui.pause()


def _complete_quest():
    ui.section("Complete Quest")
    username = ui.prompt("Username")
    p = models.find_player(db, username)
    if not p:
        ui.error("Player not found."); ui.pause(); return
    code = ui.prompt("Quest code")
    rewards = models.complete_quest(db, str(p["_id"]), code)
    if rewards:
        ui.success(f"Quest complete! Rewards: +{rewards.get('xp',0)} XP, +{rewards.get('gold',0)} Gold"
                   + (f", Item: {rewards['item']}" if rewards.get("item") else ""))
    else:
        ui.error("Could not complete quest — quest not found or not started.")
    ui.pause()


def _available_quests():
    ui.section("Available Quests for Player")
    username = ui.prompt("Username")
    p = models.find_player(db, username)
    if not p:
        ui.error("Player not found."); ui.pause(); return
    unlocked = p.get("unlocked_skills", [])
    quests   = models.get_available_quests(db, unlocked)
    rows = [
        [q["quest_code"], q["title"], q["difficulty"],
         f"XP:{q['rewards'].get('xp',0)} G:{q['rewards'].get('gold',0)}"]
        for q in quests
    ]
    ui.table(rows, ["Code", "Title", "Difficulty", "Rewards"], [18, 28, 10, 16])
    ui.pause()


# ════════════════════════════════════════════════════════════
#  ANALYTICS MENU
# ════════════════════════════════════════════════════════════

def menu_analytics():
    ui.banner(APP_TITLE, "Analytics", assignment=ASSIGNMENT, student=STUDENT_INFO)
    ui.section("Analytics (MongoDB Aggregation Pipelines)")
    choice = ui.prompt_choice([
        "Leaderboard (Top Players by XP)",
        "Skill Category Stats",
        "Quest Completion Stats",
        "<- Back",
    ])
    if choice == 1:
        ui.section("Leaderboard - Top Players by XP")
        leaders = models.leaderboard(db)
        rows = [[i+1, p["username"], p["hero_class"], p["level"], p["xp"], p["gold"]]
                for i, p in enumerate(leaders)]
        ui.table(rows, ["Rank", "Username", "Class", "Lvl", "XP", "Gold"],
                 [4, 20, 10, 4, 8, 8])
        ui.pause()
    elif choice == 2:
        _skill_analytics()
    elif choice == 3:
        ui.section("Quest Completion Stats")
        stats = models.quest_completion_stats(db)
        for status, count in stats.items():
            print(f"  {C.CYAN}{status:<20}{C.RESET}  {C.BOLD}{count}{C.RESET}")
        ui.pause()


# ════════════════════════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════════════════════════

def show_dashboard():
    ui.banner(APP_TITLE, APP_SUBTITLE, assignment=ASSIGNMENT, student=STUDENT_INFO)
    stats = models.get_summary_stats(db)
    ui.section("Dashboard")

    def stat_line(label, value, color=C.CYAN):
        print(f"  {C.DIM}{label:<32}{C.RESET} {color}{C.BOLD}{value}{C.RESET}")

    stat_line("Total Players",             stats["total_players"])
    stat_line("Total Skills in Tree",      stats["total_skills"])
    stat_line("Total Quests",              stats["total_quests"])
    stat_line("Active Quests (in-progress)", stats["active_quests"])
    stat_line("Completed Quests",          stats["completed_quests"])
    print()
    ui.info("Database: MongoDB (NoSQL)  |  Documents stored as flexible JSON")
    print()


# ════════════════════════════════════════════════════════════
#  MAIN MENU
# ════════════════════════════════════════════════════════════

def main():
    global db
    ui.enable_ansi()

    try:
        db = get_db()
        initialise_collections(db)
    except Exception:
        sys.exit(1)

    while True:
        show_dashboard()
        ui.section("Main Menu")
        choice = ui.prompt_choice([
            "[1] Players Management",
            "[2] Skill Tree Management",
            "[3] Quest Management",
            "[4] Analytics & Reports",
            "[X] Exit",
        ])
        if choice == 1:   menu_players()
        elif choice == 2: menu_skills()
        elif choice == 3: menu_quests()
        elif choice == 4: menu_analytics()
        else:
            ui.banner(APP_TITLE, "Goodbye!", assignment=ASSIGNMENT, student=STUDENT_INFO)
            print(C.MAGENTA + "  Thank you for using the Game Engine DB Demo.\n" + C.RESET)
            sys.exit(0)


if __name__ == "__main__":
    main()
