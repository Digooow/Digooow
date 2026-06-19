import os
import re
import requests
from datetime import datetime

USERNAME = "Digooow"
TOPIC = "showcase"
README_PATH = "README.md"
TOKEN = os.getenv("GITHUB_TOKEN")

headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

def get_repos_with_topic():
    url = f"https://api.github.com/search/repositories?q=user:{USERNAME}+topic:{TOPIC}"
    print(f"🔍 Buscando repositórios com tópico '{TOPIC}'...")
    response = requests.get(url, headers=headers)
    print(f"📡 Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Erro: {response.text}")
        return []
    data = response.json()
    repos = [repo["name"] for repo in data.get("items", [])]
    print(f"📦 Encontrados: {repos}")
    return repos

def generate_cards(repos):
    if not repos:
        return "<!-- Nenhum projeto encontrado com o tópico 'showcase' -->"

    # Container flexível: lado a lado com quebra de linha e espaçamento
    container_start = '<div style="display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-start;">'
    container_end = '</div>'

    cards = []
    for repo in repos:
        card_url = f"https://github-readme-stats.vercel.app/api/pin/?username={USERNAME}&repo={repo}&theme=dark&show_owner=true&description_lines_count=2"
        card_html = f'''<div style="flex: 0 0 auto;">
  <a href="https://github.com/{USERNAME}/{repo}">
    <img src="{card_url}" />
  </a>
</div>'''
        cards.append(card_html)

    # Junta todos os cards dentro do container e adiciona uma margem inferior
    return container_start + "\n".join(cards) + container_end + '\n\n<div style="clear: both; margin-bottom: 30px;"></div>'

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
    cards = generate_cards(repos)
    update_readme(cards)
