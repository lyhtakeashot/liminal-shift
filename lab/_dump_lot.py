import json
d=json.load(open("_ref/houses/houses_data.json",encoding="utf-8"))
for h in d:
    if h["id"] in ("market","shen_a4","zhou_a4","zheng_a4"):
        print(h["id"],"lot",h["lot"],"wings",h["wings"][:3],"gate",h.get("gate"),"doors",h.get("doors"))
