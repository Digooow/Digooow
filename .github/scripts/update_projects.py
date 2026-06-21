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
    return [repo["name"] for repo in data.get("items", [])]

def generate_cards(repos):
    if not repos:
        return "<!-- Nenhum projeto encontrado com o tópico 'showcase' -->"

    timestamp = int(time.time())
    cards = []
    for repo in repos:
        card_url = f"https://github-readme-stats.vercel.app/api/pin/?username={USERNAME}&repo={repo}&theme=dark&show_owner=true&description_lines_count=3&_={timestamp}"
        card_html = f'<a href="https://github.com/{USERNAME}/{repo}" style="display: inline-block; width: 49%; margin: 5px 0;">\n  <img src="{card_url}" style="width: 100%;" />\n</a>'
        cards.append(card_html)

    grouped = []
    for i in range(0, len(cards), 2):
        pair = cards[i]
        if i+1 < len(cards):
            pair += " " + cards[i+1]
        grouped.append(pair)

    return "\n".join(grouped) + '\n\n<div style="clear: both; margin-bottom: 30px;"></div>'

def update_readme(cards_html):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"(<!-- SHOWCASE-START -->)(.*?)(<!-- SHOWCASE-END -->)"
    replacement = rf"\1\n{cards_html}\n\3"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("README atualizado com sucesso!")

if __name__ == "__main__":
    repos = get_repos_with_topic()
    print(f"Repositórios encontrados: {repos}")
    cards = generate_cards(repos)
    update_readme(cards)
