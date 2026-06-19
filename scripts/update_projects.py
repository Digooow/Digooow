import os
import re
import requests

USERNAME = "Digooow"
TOPIC = "showcase"
README_PATH = "README.md"
TOKEN = os.getenv("GITHUB_TOKEN")

headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

def get_repos_with_topic():
    url = f"https://api.github.com/search/repositories?q=user:{USERNAME}+topic:{TOPIC}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    data = response.json()
    return [repo["name"] for repo in data.get("items", [])]

def generate_cards(repos):
    if not repos:
        return "<!-- Nenhum projeto encontrado -->"

    # Gera imagens lado a lado usando Markdown
    lines = []
    for i, repo in enumerate(repos):
        card_url = f"https://github-readme-stats.vercel.app/api/pin/?username={USERNAME}&repo={repo}&theme=dark&show_owner=true&description_lines_count=2"
        # Cria a imagem e o link
        img = f'<a href="https://github.com/{USERNAME}/{repo}"><img src="{card_url}" width="49%" /></a>'
        lines.append(img)

    # Junta com quebras de linha a cada 2 imagens
    result = []
    for i in range(0, len(lines), 2):
        # Pega duas imagens e coloca na mesma linha
        pair = lines[i:i+2]
        result.append(' '.join(pair))
    
    # Junta tudo com quebras de linha entre os pares
    return '\n\n'.join(result) + '\n\n<div style="margin-bottom: 30px;"></div>'

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
