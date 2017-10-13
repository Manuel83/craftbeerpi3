import requests
from git import Repo, Git

repo = Repo('./')
branch = repo.active_branch

print branch.name

for remote in repo.remotes:
    remote.fetch()

url = 'https://api.github.com/repos/manuel83/craftbeerpi3/releases'
response = requests.get(url)


result = {"branches":[], "releases": []}

result["branches"].append({"name": "master"})

for branch in repo.branches:
    result["branches"].append({"name": branch.name})

for r in response.json():
    result["releases"].append({"name": "tags/%s" % r.get("tag_name")})

print result

