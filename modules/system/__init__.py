import flask_login
import requests
import yaml
from flask import json, url_for, Response, request
from flask_classy import FlaskView, route
from flask_login import login_required, current_user
from git import Repo, Git
from modules import cbpi
import pprint
import time

from modules.login import User


class SystemView(FlaskView):
    def doShutdown(self):
        time.sleep(5)
        from subprocess import call
        call("halt")

    @login_required
    @route('/shutdown', methods=['POST'])
    def shutdown(self):
        """
        System Shutdown
        ---
        tags:
          - system
        responses:
          200:
            description: Shutdown triggered
        """
        self.doShutdown()

        return ('', 204)

    def doReboot(self):
        time.sleep(5)
        from subprocess import call
        call("reboot")

    @login_required
    @route('/reboot', methods=['POST'])
    def reboot(self):
        """
        System Reboot  
        ---
        tags:
          - system
        responses:
          200:
            description: Reboot triggered
        """
        self.doReboot()
        return ('', 204)

    @login_required
    @route('/checkout', methods=['POST'])
    def checkout_tag(self):

        data = request.json
        name = data.get("name")

        if name is None:
            return ('', 500)

        repo = Repo('./')
        repo.git.reset('--hard')
        o = repo.remotes.origin
        o.fetch()
        g = Git('./')
        g.checkout(name)
        cbpi.notify("Checkout successful", "Please restart the system")
        return ('', 204)


    @login_required
    @route('/git/status', methods=['GET'])
    def git_status(self):

        repo = Repo('./')

        o = repo.remotes.origin
        o.fetch()

        branch = repo.active_branch

        url = 'https://api.github.com/repos/manuel83/craftbeerpi3/releases'
        response = requests.get(url)

        result = {"current_branch": branch.name, "branches": [], "releases": []}
        result["branches"].append({"name": "master"})

        for branch in repo.branches:
            result["branches"].append({"name": branch.name})

        for r in response.json():
            result["releases"].append({"name": "tags/%s" % r.get("tag_name")})

        """
        Check for GIT status
        ---
        tags:
          - system
        responses:
          200:
            description: Git Status
        """
        return json.dumps(result)

    @login_required
    @route('/check_update', methods=['GET'])
    def check_update(self):
        """
        Check for GIT update
        ---
        tags:
          - system
        responses:
          200:
            description: Git Changes
        """
        repo = Repo('./')
        o = repo.remotes.origin
        o.fetch()
        changes = []
        commits_behind = repo.iter_commits('master..origin/master')

        for c in list(commits_behind):
            changes.append({"committer": c.committer.name, "message": c.message})

        return json.dumps(changes)

    @login_required
    @route('/git/pull', methods=['POST'])
    def update(self):
        """
        System Update
        ---
        tags:
          - system
        responses:
          200:
            description: Git Pull Triggered
        """
        repo = Repo('./')
        o = repo.remotes.origin
        info = o.pull()
        cbpi.notify("Pull successful", "The lasted updated was downloaded. Please restart the system")
        return ('', 204)

    @route('/connect', methods=['GET'])
    def connect(self):
        """
        Connect
        ---
        tags:
          - system
        responses:
          200:
            description: CraftBeerPi System Cache
        """
        if cbpi.get_config_parameter("password_security", "NO") == "NO":
            user = User()
            user.id = "craftbeerpi"
            flask_login.login_user(user)

        if self.api.get_config_parameter("setup", "YES") == "YES":
            return json.dumps(dict(setup=True, loggedin= current_user.is_authenticated ))
        else:
            return json.dumps(dict(setup=False, loggedin= current_user.is_authenticated))

    @login_required
    @route('/dump', methods=['GET'])
    def dump(self):
        """
        Dump Cache
        ---
        tags:
          - system
        responses:
          200:
            description: CraftBeerPi System Cache
        """
        return Response(response=json.dumps(cbpi.cache, sort_keys=True, indent=4), status=200, mimetype='application/json')



@cbpi.addon.core.initializer()
def init(cbpi):

    SystemView.api = cbpi
    SystemView.register(cbpi.web, route_base='/api/system')
