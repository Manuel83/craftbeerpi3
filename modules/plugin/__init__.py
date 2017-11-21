import sys
from flask import  request, send_from_directory, json
from importlib import import_module
from modules.core.core import cbpi
from git import Repo
import os
import requests
import yaml
import shutil
from flask_classy import FlaskView, route

modules = {}

class PluginView(FlaskView):


    def merge(self, source, destination):
        """
        Helper method to merge two dicts
        :param source:
        :param destination:
        :return:
        """
        for key, value in source.items():
            if isinstance(value, dict):
                   # get node or create one
                node = destination.setdefault(key, {})
                self.merge(value, node)
            else:
                destination[key] = value

        return destination


    @route('/', methods=['GET'])
    def get(self):
        """
        Get Plugin List
        ---
        tags:
          - plugin
        responses:
          200:
            description: List of all plugins
        """
        response = requests.get("https://raw.githubusercontent.com/Manuel83/craftbeerpi-plugins/master/plugins.yaml")
        self.api.cache["plugins"] = self.merge(yaml.load(response.text), self.api.cache["plugins"])
        for key, value in  cbpi.cache["plugins"].iteritems():
            print key
            value["installed"] = os.path.isdir("./plugins/%s/" % (key))
        return json.dumps(cbpi.cache["plugins"])


    @route('/<name>', methods=['DELETE'])
    def delete(self,name):
        """
        Delete Plugin
        ---
        tags:
          - plugin
        parameters:
          - in: path
            name: name
            schema:
              type: string
            required: true
            description: Plugin name 
        responses:
          200:
            description: Plugin deleted
        """
        if os.path.isdir("./plugins/"+name) is False:
            return ('Dir not found', 500)
        shutil.rmtree("./plugins/"+name)
        cbpi.notify("Plugin deleted", "Plugin %s deleted successfully" % name)
        return ('', 204)

    @route('/<name>/download', methods=['POST'])
    def download(self, name):
        """
        Download Plugin
        ---
        tags:
          - plugin
        parameters:
          - in: path
            name: name
            schema:
              type: string
            required: true
            description: Plugin name 
        responses:
          200:
            description: Plugin downloaded
        """
        plugin = self.api.cache["plugins"].get(name)
        plugin["loading"] = True
        if plugin is None:
            return ('', 404)
        try:
            Repo.clone_from(plugin.get("repo_url"), "./modules/plugins/%s/" % (name))
            self.api.notify("Download successful", "Plugin %s downloaded successfully" % name)
        finally:
            plugin["loading"] = False
        return ('', 204)

    @route('/<name>/update', methods=['POST'])
    def update(self, name):
        """
        Pull Plugin Update
        ---
        tags:
          - plugin
        parameters:
          - in: path
            name: name
            schema:
              type: string
            required: true
            description: Plugin name 
        responses:
          200:
            description: Plugin updated
        """
        repo = Repo("./modules/plugins/%s/" % (name))
        o = repo.remotes.origin
        info = o.pull()
        self.api.notify("Plugin Updated", "Plugin %s updated successfully. Please restart the system" % name)
        return ('', 204)





@cbpi.addon.core.initializer()
def init(cbpi):
    cbpi.cache["plugins"] = {}
    PluginView.api = cbpi
    PluginView.register(cbpi._app, route_base='/api/plugin')