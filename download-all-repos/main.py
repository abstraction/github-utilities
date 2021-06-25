"""
Download and delete all Github repositories
- Replace credentials in .env
- Replace credentials below
- Run
"""

import csv

import requests
from dotenv import dotenv_values
from git import Repo

TOTAL = 500  # Number of repositories
CSV_PATH = '/Users/<user>/Desktop'  # P.S. No trailing /

# Don't change anything below here.

config = dotenv_values(".env")
PAGES = round(TOTAL / 100)
i = 0

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'token {config["API_TOKEN"]}',
}

if __name__ == '__main__':
    while i <= PAGES:
        response = requests.get(f'https://api.github.com/user/repos?page={i}&per_page=100', headers=headers)
        for repos in response.json():
            repo = f'https://{config["USER"]}:{config["API_TOKEN"]}@github.com/{config["USER"]}/{repos["name"]}.git'
            repo_name = repos['name']
            repo_description = repos['description']
            try:
                print(f'♻️ Cloning {repo}...')
                Repo.clone_from(repo, f'{CSV_PATH}/repository/{repo_name}')
                with open(f'{CSV_PATH}/success_repos.csv', mode='a') as repo_csv:
                    repo_writer = csv.writer(repo_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    repo_writer.writerow([repo_name, repo_description])
                response = requests.delete(f'https://api.github.com/repos/{config["USER"]}/{repo_name}',
                                           headers=headers)
                if response.status_code == 204:
                    print(f'💥 Deleted {repo}!')
            except Exception:
                with open(f'{CSV_PATH}/failed_repos.csv', mode='a') as repo_csv:
                    repo_writer = csv.writer(repo_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    repo_writer.writerow([repo_name, repo_description])
        i += 1
