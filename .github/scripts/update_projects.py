from __future__ import annotations

import os
import re
import sys
import time

import requests

USERNAME: str = "Digooow"
TOPIC: str = "showcase"
README_PATH: str = "README.md"
TOKEN: str | None = os.getenv("GITHUB_TOKEN")
REQUEST_TIMEOUT_SECONDS: int = 15

VERCEL_DOMAIN: str = "github-readme-stats-eta-brown-33.vercel.app"

headers: dict[str, str] = {
    "Accept": "application/vnd.github+json",
    **({"Authorization": f"token {TOKEN}"} if TOKEN else {}),
}


def get_repos_with_topic() -> list[str]:
    repos_encontrados: list[str] = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/users/{USERNAME}/repos"
            f"?type=owner&sort=updated&direction=desc&per_page=100&page={page}"
        )
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            print(
                f"Erro de rede ao consultar a API do GitHub: {exc}",
                file=sys.stderr,
            )
            raise SystemExit(1) from exc

        if response.status_code != 200:
            print(
                f"Erro ao buscar repositórios (HTTP {response.status_code}): {response.text}",
                file=sys.stderr,
            )
            raise SystemExit(1)

        data = response.json()
        if not isinstance(data, list):
            print(
                "Resposta inesperada da API do GitHub (esperado array JSON).",
                file=sys.stderr,
            )
            raise SystemExit(1)

        if not data:
            break

        for repo in data:
            topics = repo.get("topics", [])
            name = repo.get("name")
            if isinstance(name, str) and isinstance(topics, list) and TOPIC in topics:
                repos_encontrados.append(name)

        page += 1

    return repos_encontrados


def generate_cards(repos: list[str]) -> str:
    if not repos:
        return "<!-- Nenhum projeto encontrado com o tópico 'showcase' -->"

    cache_buster = int(time.time())
    lines: list[str] = []

    for i in range(0, len(repos), 2):
        lines.append("  <tr>")
        repo1 = repos[i]
        url1 = (
            f"https://{VERCEL_DOMAIN}/api/pin/?username={USERNAME}&repo={repo1}"
            f"&theme=dark&show_owner=true&description_lines_count=2&_={cache_buster}"
        )
        lines.append(
            f'    <td><a href="https://github.com/{USERNAME}/{repo1}"><img src="{url1}" /></a></td>'
        )

        if i + 1 < len(repos):
            repo2 = repos[i + 1]
            url2 = (
                f"https://{VERCEL_DOMAIN}/api/pin/?username={USERNAME}&repo={repo2}"
                f"&theme=dark&show_owner=true&description_lines_count=2&_={cache_buster}"
            )
            lines.append(
                f'    <td><a href="https://github.com/{USERNAME}/{repo2}"><img src="{url2}" /></a></td>'
            )
        else:
            lines.append("    <td></td>")

        lines.append("  </tr>")

    return "\n".join(lines)


def update_readme(cards_html: str) -> None:
    with open(README_PATH, encoding="utf-8") as f:
        content = f.read()

    pattern = r"(<!-- SHOWCASE-START -->)(.*?)(<!-- SHOWCASE-END -->)"
    if not re.search(pattern, content, flags=re.DOTALL):
        print(
            "Marcadores <!-- SHOWCASE-START --> / <!-- SHOWCASE-END --> não encontrados no README.md.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    replacement = rf"\1\n{cards_html}\n\3"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✅ README atualizado com sucesso!")


if __name__ == "__main__":
    repos = get_repos_with_topic()
    if not repos:
        print(
            "Nenhum repositório com tópico 'showcase' retornado; preservando README.md atual.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print(f"📦 Repositórios encontrados: {repos}")
    cards = generate_cards(repos)
    update_readme(cards)
