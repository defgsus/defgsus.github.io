import os
import datetime
from pathlib import Path
from cache import Cache
import yaml
from jinja2 import Template, Environment, FileSystemLoader
import markdown

PROJECT_PATH = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = PROJECT_PATH / "templates"
OUTPUT_PATH = PROJECT_PATH / "docs"


def get_repo_list():
    repo_list = Cache.load("repo_list")
    return sorted(
        filter(lambda r: r["owner"]["login"] == "defgsus", repo_list),
        key=lambda r: r["created_at"],
        reverse=True,
    )


def get_repo_descs():
    data = yaml.safe_load((TEMPLATE_PATH / "repo-descriptions.yaml").read_text())
    data = {
        key: {
            key2: markdown.markdown(value2)
            for key2, value2 in value.items()
        }
        for key, value in data.items()
    }
    return data


def get_template_env():
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_PATH)
    )
    return env


def update_repo_yaml():
    repo_list = get_repo_list()
    # repo_info = get_repo_descs()

    with open(TEMPLATE_PATH / "repo-descriptions.yaml", "w") as fp:
        for repo in (repo_list):
            print(f"{repo['name']}:", file=fp)
            print(f"  short_desc: |", file=fp)
            print(f"    {repo['description']}", file=fp)
            print(f"  long_desc: ''\n", file=fp)


def render_index():
    env = get_template_env()
    template = env.get_template("repo-index.html")
    repo_list = get_repo_list()
    repo_descs = get_repo_descs()
    render_rows = []

    last_year = None
    for repo in repo_list:
        year = repo["created_at"][:4]

        row = {
            "name": repo["name"],
            "language": repo["language"],
            "date_created": repo["created_at"][:10],
            "date_updated": repo["updated_at"][:10],
            "short_description": repo_descs[repo["name"]]["short_desc"].strip(),
            "long_description": repo_descs[repo["name"]]["long_desc"].strip() or None,
            "url": repo["html_url"],
        }

        if year != last_year:
            row["year"] = year
        last_year = year

        render_rows.append(row)

    markup = template.render(**{
        "meta": {
            "title": "Index Repium",
            "description": "Index of repos on github, by good ol' def.gsus-",
        },
        "repo_list": render_rows,
    })

    os.makedirs(OUTPUT_PATH, exist_ok=True)
    (OUTPUT_PATH / "index.html").write_text(markup)


if __name__ == "__main__":
    # update_repo_yaml()  # CAREFUL! This overwrites the existing yaml
    render_index()
