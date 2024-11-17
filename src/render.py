import os
import datetime
import json
from pathlib import Path
from cache import Cache
import glob

import yaml
import markdown
import scss
from jinja2 import Template, Environment, FileSystemLoader

PROJECT_PATH = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = PROJECT_PATH / "templates"
OUTPUT_PATH = PROJECT_PATH / "docs"

LANGUAGE_MAPPING = {
    "Python": "python",
    "C++": "cpp",
    "Jupyter Notebook": "jupyter",
    "HTML": "html",
    "JavaScript": "js",
    "GLSL": "glsl",
}


def get_repo_list():
    repo_list = Cache.load("repo_list")
    return sorted(
        filter(
            lambda r: r["owner"]["login"] == "defgsus" or r["name"] in ("elastipy", "shatrabase"),
            repo_list,
        ),
        key=lambda r: r["created_at"],
        reverse=True,
    )


def get_repo_infos():
    data = yaml.safe_load((TEMPLATE_PATH / "repo-infos.yaml").read_text())
    data = {
        key: {
            key2: markdown.markdown(value2) if "desc" in key2 else value2
            for key2, value2 in value.items()
        }
        for key, value in data.items()
    }
    return data


def get_repo_commits():
    commits = {}
    for fn in sorted(glob.glob(str(Cache.PATH / "commits" / "*" / "*.json"))):
        _, name = fn.split("/")[-2:]
        name = name[:-5]
        commits[name] = commits.get(name, []) + json.loads(Path(fn).read_text())

    for v in commits.values():
        #print(json.dumps(v[0], indent=2))
        v.sort(key=lambda c: c["commit"]["committer"]["date"])

    return commits


def get_repo_dates():
    all_commits = get_repo_commits()
    repo_dates = {}
    for name, commits in all_commits.items():
        repo_dates[name] = (
            commits[0]["commit"]["committer"]["date"],
            commits[-1]["commit"]["committer"]["date"]
        )
    return repo_dates


def get_template_env():
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_PATH)
    )
    return env


def update_repo_yaml():
    repo_list = get_repo_list()
    # repo_info = get_repo_descs()

    with open(TEMPLATE_PATH / "repo-infos.yaml", "w") as fp:
        for repo in repo_list:
            print(f"{repo['name']}:", file=fp)
            print(f"  short_desc: |", file=fp)
            print(f"    {repo['description']}", file=fp)
            print(f"  long_desc: ''\n", file=fp)


def render_index():
    env = get_template_env()
    template = env.get_template("repo-index.html")
    repo_list = get_repo_list()
    repo_infos = get_repo_infos()
    repo_dates = get_repo_dates()
    tag_images = set(n.split("/")[-1][:-4] for n in glob.glob(str(OUTPUT_PATH / "img" / "tags" / "*.png")))

    missing_infos = []
    for repo in repo_list:
        if repo["name"] not in repo_infos:
            missing_infos.append(repo)

    if missing_infos:
        print("Missing repos in templates/repo-infos.yaml. Add them with:\n")
        for repo in missing_infos:
            print(
                f"{repo['name']}:\n"
                f"  categories:\n"
                f"  short_desc: {repo['description']}\n"
                f"  long_desc: ''"
            )
        exit(1)

    repos_by_year = {}
    for repo in repo_list:
        repo_info = repo_infos[repo["name"]]

        if repo_info.get("hide"):
            continue

        try:
            year = repo["created_at"][:4]

            date_first = repo_dates[repo["name"]][0][:10]
            date_last = repo_dates[repo["name"]][-1][:10]

            year = date_first[:4]

            if date_first == date_last:
                date_str = date_first
            elif (datetime.date.today() - datetime.datetime.strptime(date_last, "%Y-%m-%d").date()).days < 30:
                date_str = f"{date_first} to now"
            else:
                if date_first[:4] == date_last[:4]:
                    date_last = date_last[5:]
                date_str = f"{date_first} to {date_last}"

            tags = sorted(repo_info["categories"].split())

            row = {
                "name": repo["name"],
                "language": repo_info.get("language") or LANGUAGE_MAPPING[repo["language"]],
                "tags": tags,
                "dates": date_str.replace("-", "/"),
                "short_description": repo_info["short_desc"].strip(),
                "long_description": repo_info["long_desc"].strip() or None,
                "url": repo["html_url"],
            }

            year_repos, year_tags = repos_by_year.setdefault(year, ([], set()))
            year_repos.append(row)
            for tag in tags:
                year_tags.add(tag)

        except:
            print("IN REPO", repo["name"])
            raise

    for year, (repos, tags) in repos_by_year.items():
        repos_by_year[year] = (repos, " ".join(sorted(tags)))

    repos_by_year = {
        year: repos_by_year[year]
        for year in sorted(repos_by_year, reverse=True)
    }

    markup = template.render(**{
        "meta": {
            "title": "Index Repium",
            "description": "Index of repos on github, by good ol' def.gsus-",
            "scripts": ("js/repos.js", ),
        },
        "repos_by_year": repos_by_year,
    })

    os.makedirs(OUTPUT_PATH, exist_ok=True)
    (OUTPUT_PATH / "index.html").write_text(markup)


def render_style():
    c = scss.Compiler(output_style="compressed")
    src = c.compile(str(TEMPLATE_PATH / "style.scss"))
    (OUTPUT_PATH / "style.css").write_text(src)


if __name__ == "__main__":
    # update_repo_yaml()  # CAREFUL! This overwrites the existing yaml
    render_index()
    render_style()
