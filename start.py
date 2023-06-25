import requests
import json
import time
from bs4 import BeautifulSoup

skills = [
    "Attack", "Strength", "Defence", "Ranged", "Prayer", "Magic", "Runecraft",
    "Hitpoints", "Crafting", "Mining", "Smithing", "Fishing", "Cooking",
    "Firemaking", "Woodcutting", "Slayer"
]

# Send a GET request to the web page
url = "https://oldschool.runescape.wiki/w/Quests/List"
response = requests.get(url)

# Create a BeautifulSoup object to parse the HTML content
soup = BeautifulSoup(response.text, "html.parser")

# Find the table containing the quest list
table = soup.find_all("table", class_="sortable")

# Extract information from the table
rows = []
rows.extend(table[0].find_all("tr"))
rows.extend(table[1].find_all("tr"))

# Get the quest names from the rows
quests = []
for row in rows[1:]:
    cells = row.find_all("td")
    if len(cells) >= 2:
        quest_name = cells[1].find("a").text.strip()
        quests.append(quest_name)

quest_json = []

for i, quest_name in enumerate(quests, start=1):
    url = f"https://oldschool.runescape.wiki/w/{quest_name.replace(' ', '_')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="questdetails")

    rows = table.find_all("tr")

    quest_start = rows[0].find_all("td")[0].text.strip().replace("Show on map", "")
    quest_desc = rows[2].find_all("td")[0].text.strip()
    quest_diff = rows[1].find_all("td")[0].text.strip()
    quest_length = rows[3].find_all("td")[0].text.strip()

    rewards = []
    rewards_section = soup.find("h2", text="Rewards")
    if rewards_section:
        rewards_list = rewards_section.find_next_sibling("ul")
        if rewards_list:
            rewards = [reward.strip().replace("experience", "exp") for reward in rewards_list.text.strip().split("\n")]

    qp_req = 0
    quest_req = []
    items_req = rows[5].find_all("td")[0].text.strip().split("\n")

    reqs = rows[4].find_all("td")[0].text.strip()
    req = reqs.split("\n")

    for element in req:
        if "Quest points" in element:
            qp_req = int("".join(filter(str.isdigit, element)))
            break

    skill_req = []
    for element in req:
        for skill in skills:
            if skill in element:
                element = element.lstrip()
                if element[0].isdigit():
                    temp = element.split(" ")
                    boostable = temp[2] == "(boostable)"
                    skill_req.append({"skill": temp[1], "level": int(temp[0]), "boostable": boostable})
        for quest in quests:
            if quest in element:
                quest_req.append(element)

    requirements = {
        "quest_points": qp_req,
        "quests": quest_req,
        "skills": skill_req,
        "items": items_req
    }

    quest_data = {
        "start": quest_start,
        "name": quest_name.replace("_", " "),
        "description": quest_desc,
        "difficulty": quest_diff,
        "length": quest_length,
        "requirements": requirements,
        "rewards": rewards
    }
    quest_json.append(quest_data)

    percentage = (i / len(quests)) * 100
    print(f"{i}/{len(quests)} ({percentage:.2f}%)")

    # This is just here to not overload the OSRS WIKI with too much traffic at once, idk if this makes any difference though... xd
    if i < len(quests):
        time.sleep(3)

with open("quests.json", "w") as file:
    json.dump(quest_json, file)

print("DONE")
