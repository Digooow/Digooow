import os
import re
import requests
import time

USERNAME = "Digooow"
TOPIC = "showcase"
README_PATH = "README.md"
TOKEN = os.getenv("GITHUB_TOKEN")

headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}
if not TOKEN:
    print("⚠️  GITHUB_TOKEN não definido. Limite de requisições reduzido.")

def get_repos_with_topic():
    url = f"https://api.github.com/search/repositories?q=user:{USERNAME}+topic:{TOPIC}&sort=updated&order=desc"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erro ao buscar repositórios: {response.status_code}")
        return []
    data = response.json()
    repos = []
    for item in data.get("items", []):
        repos.append({
            "name": item["name"],
            "description": item.get("description", "").strip()
        })
    return repos

def generate_cards(repos):
    if not repos:
        return "<!-- Nenhum projeto encontrado com o tópico 'showcase' -->"

    cache_buster = int(time.time())

    cards = []
    for repo in repos:
        name = repo["name"]
        card_url = f"https://github-readme-stats.vercel.app/api/pin/?username={USERNAME}&repo={name}&theme=dark&show_owner=true&description_lines_count=2&_={cache_buster}"
        card_html = f'<a href="https://github.com/{USERNAME}/{repo}">\n  <img align="left" src="{card_url}" />\n</a>\n'
        cards.append(card_html)

    return "\n".join(cards) + '\n\n<div style="clear: both; margin-bottom: 30px;"></div>'

def update_readme(cards_html):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"(<!-- SHOWCASE-START -->)(.*?)(<!-- SHOWCASE-END -->)"
    replacement = rf"\1\n{cards_html}\n\3"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✅ README atualizado com sucesso!")

if __name__ == "__main__":
    repos = get_repos_with_topic()
    print(f"📦 Repositórios encontrados: {[r['name'] for r in repos]}")
    cards = generate_cards(repos)
    update_readme(cards)
