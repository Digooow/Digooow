from __future__ import annotations

import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

README_PATH = Path("README.md")
START_MARKER = "<!--START_SECTION:badges-->"
END_MARKER = "<!--END_SECTION:badges-->"
BADGE_WIDTH_PX = 80

SECTION_PATTERN = re.compile(
    rf"({re.escape(START_MARKER)})(.*?)({re.escape(END_MARKER)})",
    flags=re.DOTALL,
)

MARKDOWN_BADGE_PATTERN = re.compile(
    r"^\[!\[(?P<title>.+?)\]\((?P<img>https?://[^\s)]+)\)\]\((?P<href>https?://[^\s)]+)\)$"
)


@dataclass(frozen=True)
class Badge:
    title: str
    img_url: str
    href_url: str


def is_safe_http_url(url: str) -> bool:
    """Validate that URL uses http/https scheme with a valid host."""
    parsed = urlsplit(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def parse_markdown_badges(section_body: str) -> list[Badge] | None:
    """Parse Markdown badge lines; return None if section is already HTML-formatted."""
    lines = [line.strip() for line in section_body.splitlines() if line.strip()]
    if not lines:
        return None

    badges: list[Badge] = []
    has_markdown = False
    has_non_markdown = False

    for line in lines:
        match = MARKDOWN_BADGE_PATTERN.match(line)
        if not match:
            has_non_markdown = True
            continue

        has_markdown = True
        raw_title = match.group("title").replace('\\"', '"')
        img_url = match.group("img")
        href_url = match.group("href")

        if not (is_safe_http_url(img_url) and is_safe_http_url(href_url)):
            raise ValueError(f"URL inválida detectada na badge: {line}")

        badges.append(Badge(title=raw_title, img_url=img_url, href_url=href_url))

    if not has_markdown:
        return None

    if has_non_markdown:
        raise ValueError(
            "Conteúdo misto inesperado dentro da seção de badges; abortando para evitar perda de dados."
        )

    return badges


def render_badges_html(badges: list[Badge], newline: str) -> str:
    """Render Credly badges as aligned HTML links with fixed image width."""
    items = [
        (
            f'  <a href="{html.escape(badge.href_url, quote=True)}">'
            f'<img src="{html.escape(badge.img_url, quote=True)}" '
            f'alt="{html.escape(badge.title, quote=True)}" '
            f'width="{BADGE_WIDTH_PX}" /></a>'
        )
        for badge in badges
    ]
    return newline.join(['<p align="left">', *items, "</p>"])


def format_readme_content(content: str) -> tuple[str, bool]:
    """Convert Markdown Credly badges in README content to fixed-width HTML."""
    match = SECTION_PATTERN.search(content)
    if not match:
        raise ValueError(f"Marcadores {START_MARKER} / {END_MARKER} não encontrados.")

    newline = "\r\n" if "\r\n" in content else "\n"
    section_body = match.group(2)
    badges = parse_markdown_badges(section_body)
    if badges is None:
        return content, False

    rendered_html = render_badges_html(badges, newline=newline)
    replacement = f"{match.group(1)}{newline}{rendered_html}{newline}{match.group(3)}"
    updated = f"{content[:match.start()]}{replacement}{content[match.end():]}"
    return updated, updated != content


def main() -> int:
    if not README_PATH.is_file():
        print(f"Arquivo {README_PATH} não encontrado.", file=sys.stderr)
        return 1

    with README_PATH.open("r", encoding="utf-8", newline="") as file:
        original_content = file.read()

    try:
        updated_content, changed = format_readme_content(original_content)
    except ValueError as exc:
        print(f"Erro ao formatar badges: {exc}", file=sys.stderr)
        return 1

    if not changed:
        print("ℹ️ Badges já estão formatadas com tamanho fixo.")
        return 0

    with README_PATH.open("w", encoding="utf-8", newline="") as file:
        file.write(updated_content)

    print("✅ Badges Credly convertidas para HTML com width=80.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
