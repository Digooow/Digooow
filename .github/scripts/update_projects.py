import os
import re
import requests
import time

USERNAME = "Digooow"
TOPIC = "showcase"
README_PATH = "README.md"
TOKEN = os.getenv("GITHUB_TOKEN")

VERCEL_DOMAIN = "github-readme-stats-eta-brown-33.vercel.app"

headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

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

    cache_buster = int(time.time())
    lines = []

    for i in range(0, len(repos), 2):
        lines.append("  <tr>")
        repo1 = repos[i]
        url1 = f"https://{VERCEL_DOMAIN}/api/pin/?username={USERNAME}&repo={repo1}&theme=dark&show_owner=true&description_lines_count=2&_={cache_buster}"
        lines.append(f'    <td><a href="https://github.com/{USERNAME}/{repo1}"><img src="{url1}" /></a></td>')

        if i+1 < len(repos):
            repo2 = repos[i+1]
            url2 = f"https://{VERCEL_DOMAIN}/api/pin/?username={USERNAME}&repo={repo2}&theme=dark&show_owner=true&description_lines_count=2&_={cache_buster}"
            lines.append(f'    <td><a href="https://github.com/{USERNAME}/{repo2}"><img src="{url2}" /></a></td>')
        else:
            lines.append('    <td></td>')

        lines.append("  </tr>")

    return "\n".join(lines)

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
    print(f"📦 Repositórios encontrados: {repos}")
    cards = generate_cards(repos)
    update_readme(cards)
