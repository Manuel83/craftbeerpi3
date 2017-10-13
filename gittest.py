import requests
from git import Repo, Git

repo = Repo('./')
print repo
for remote in repo.remotes:

    remote.fetch()

url = 'https://api.github.com/repos/manuel83/craftbeerpi3/releases'
response = requests.get(url)

result = []

for r in response.json():
    result.append({"tag_name": r.get("tag_name"), "timestamp": r.get("created_at")})

print result