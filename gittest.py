from git import Repo, Git

repo = Repo('./')
print repo
for remote in repo.remotes:
    print remote
    remote.fetch()ls
