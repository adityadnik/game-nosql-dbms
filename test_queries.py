"""Quick smoke test for all queries."""
from database import get_db, initialise_collections
from models import (get_all_players, get_all_skills, get_all_quests,
                    leaderboard, skill_category_stats, quest_completion_stats,
                    get_summary, find_player, get_available_skills,
                    get_available_quests, get_player_progress)

db = get_db()
initialise_collections(db)

print("=== PLAYERS ===")
for p in get_all_players(db):
    print(f"  {p['username']:20} Lvl:{p['level']}  XP:{p['xp']}  Gold:{p['gold']}")

print("\n=== SKILLS (partial) ===")
for s in get_all_skills(db)[:5]:
    print(f"  {s['skill_code']:16} {s['name']:28} prereqs:{s['prerequisites']}")

print("\n=== QUESTS ===")
for q in get_all_quests(db):
    print(f"  {q['quest_code']:18} {q['title']:36} {q['difficulty']}")

print("\n=== LEADERBOARD ===")
for i, p in enumerate(leaderboard(db), 1):
    print(f"  #{i}  {p['username']:20} XP:{p['xp']}")

print("\n=== SKILL CATEGORY ANALYTICS ===")
for s in skill_category_stats(db):
    print(f"  {s['_id']:12} count:{s['total_skills']}  avg_xp:{int(s['avg_xp_cost'])}")

print("\n=== QUEST COMPLETION STATS ===")
print(" ", quest_completion_stats(db))

print("\n=== SUMMARY ===")
for k, v in get_summary(db).items():
    print(f"  {k:<30} {v}")

print("\n=== AVAILABLE SKILLS FOR PriyaMage ===")
p = find_player(db, "PriyaMage")
for s in get_available_skills(db, p["unlocked_skills"]):
    print(f"  {s['skill_code']:16} {s['name']}")

print("\n=== AVAILABLE QUESTS FOR AaravWarrior ===")
p2 = find_player(db, "AaravWarrior")
for q in get_available_quests(db, p2["unlocked_skills"]):
    print(f"  {q['quest_code']:18} {q['title']}")
