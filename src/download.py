from github import Github

from credentials import GITHUB_ACCESS_TOKEN
from cache import Cache


def download_repo_list():
    api = Github(GITHUB_ACCESS_TOKEN)

    Cache.store("repo_list", [r.raw_data for r in api.get_user().get_repos()])


if __name__ == "__main__":
    download_repo_list()
