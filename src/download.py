import datetime

from github import Github
from tqdm import tqdm

from credentials import GITHUB_ACCESS_TOKEN
from cache import Cache


def to_datetime(d: str) -> datetime.datetime:
    return datetime.datetime.strptime(d[:19], "%Y-%m-%dT%H:%M:%S")


def download_repo_list():
    if not Cache.exists("repo_list"):
        api = Github(GITHUB_ACCESS_TOKEN)
        Cache.store("repo_list", [r.raw_data for r in tqdm(api.get_user().get_repos())])


def download_commits():
    repo_list = Cache.load("repo_list")

    api = Github(GITHUB_ACCESS_TOKEN)
    api2 = Github(GITHUB_ACCESS_TOKEN, per_page=1)

    for repo in repo_list:
        date_created = to_datetime(repo["created_at"])

        cache_name = f"commits/first/{repo['name']}"
        if not Cache.exists(cache_name):
            commits = api.get_repo(repo["id"]).get_commits(
                until=date_created + datetime.timedelta(days=1)
            ).get_page(0)
            Cache.store(cache_name, [c.raw_data for c in commits])
            print(f"rate-limit: {api.rate_limiting[0]}/{api.rate_limiting[1]}")

        cache_name = f"commits/last/{repo['name']}"
        if not Cache.exists(cache_name):
            commits = api2.get_repo(repo["id"]).get_commits().get_page(0)
            Cache.store(cache_name, [c.raw_data for c in commits])
            print(
                f"rate-limit: {api2.rate_limiting[0]}/{api2.rate_limiting[1]} "
                f"({datetime.datetime.fromtimestamp(api2.rate_limiting_resettime)})"
            )


if __name__ == "__main__":
    download_repo_list()
    download_commits()
