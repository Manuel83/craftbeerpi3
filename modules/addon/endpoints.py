import json

import sys
from flask import Blueprint, request, send_from_directory
from importlib import import_module
from modules import socketio, cbpi


from git import Repo
import os
import requests
import yaml
import shutil

blueprint = Blueprint('addon', __name__)


modules = {}

def merge(source, destination):
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
            merge(value, node)
        else:
            destination[key] = value

    return destination

@blueprint.route('/', methods=['GET'])
def getPlugins():
    """
    Endpoint for all plugins
    :return:
    """
    result = []
    for filename in os.listdir("./modules/plugins"):
        if filename.endswith(".DS_Store") or filename.endswith(".py") or filename.endswith(".pyc"):
            continue
        result.append(filename)

    return json.dumps(result)

@blueprint.route('/<name>', methods=['GET'])
def getFile(name):
    """
    Returns plugin code
    :param name: plugin name
    :return: the plugin code from __init__.py
    """
    return send_from_directory('./plugins/'+name, "__init__.py")

@blueprint.route('/<name>', methods=['PUT'])
def createPlugin(name):

    """
    Create a new plugin file
    :param name: the plugin name
    :return: empty http response 204
    """
    if not os.path.exists("./modules/plugins/"+name):
        os.makedirs("./modules/plugins/"+name)
        with open("./modules/plugins/" + name + "/__init__.py", "wb") as fo:
            fo.write("")
        cbpi.emit_message("PLUGIN %s CREATED" % (name))
        return ('', 204)
    else:
        cbpi.emit_message("Failed to create plugin %s. Name arlready in use" % (name))
        return ('', 500)




@blueprint.route('/<name>', methods=['POST'])
def saveFile(name):

    """
    save plugin code. code is provides via http body
    :param name: the plugin name
    :return: empty http reponse
    """
    with open("./modules/plugins/"+name+"/__init__.py", "wb") as fo:
        fo.write(request.get_data())
    cbpi.emit_message("PLUGIN %s SAVED" % (name))

    return ('', 204)

@blueprint.route('/<name>', methods=['DELETE'])
def deletePlugin(name):

    """
    Delete plugin
    :param name: plugin name
    :return: HTTP 204 if ok - HTTP 500 if plugin not exists
    """
    if os.path.isdir("./modules/plugins/"+name) is False:
        return ('Dir Not found', 500)
    shutil.rmtree("./modules/plugins/"+name)
    cbpi.notify("Plugin deleted", "Plugin %s deleted successfully" % name)
    return ('', 204)

@blueprint.route('/<name>/reload/', methods=['POST'])
def reload(name):
    """
    hot reload plugnin
    :param name:
    :return:
    """
    try:
        if name in cache["modules"]:
            reload(cache["modules"][name])
            cbpi.emit_message("REALOD OF PLUGIN %s SUCCESSFUL" % (name))
            return ('', 204)
        else:
            cache["modules"][name] = import_module("modules.plugins.%s" % (name))
            return ('', 204)
    except Exception as e:
        cbpi.emit_message("REALOD OF PLUGIN %s FAILED" % (name))
        return json.dumps(e.message)


@blueprint.route('/list', methods=['GET'])
def plugins():
    """
    Read the central plugin yaml to get a list of all official plugins
    :return:
    """
    response = requests.get("https://raw.githubusercontent.com/Manuel83/craftbeerpi-plugins/master/plugins.yaml")
    cbpi.cache["plugins"] = merge(yaml.load(response.text), cbpi.cache["plugins"])
    for key, value in  cbpi.cache["plugins"].iteritems():
        value["installed"] = os.path.isdir("./modules/plugins/%s/" % (key))

    return json.dumps(cbpi.cache["plugins"])


@blueprint.route('/<name>/download', methods=['POST'])
def download_addon(name):

    plugin = cbpi.cache["plugins"].get(name)
    plugin["loading"] = True
    if plugin is None:
        return ('', 404)
    try:
        Repo.clone_from(plugin.get("repo_url"), "./modules/plugins/%s/" % (name))
        cbpi.notify("Download successful", "Plugin %s downloaded successfully" % name)
    finally:
        plugin["loading"] = False

    return ('', 204)

@blueprint.route('/<name>/update', methods=['POST'])
def update_addon(name):
    repo = Repo("./modules/plugins/%s/" % (name))
    o = repo.remotes.origin
    info = o.pull()
    cbpi.notify("Plugin Updated", "Plugin %s updated successfully. Please restart the system" % name)
    return ('', 204)


def loadCorePlugins():
    for filename in os.listdir("./modules/base_plugins"):


        if os.path.isdir("./modules/base_plugins/"+filename) is False:
            continue
        try:
            modules[filename] = import_module("modules.base_plugins.%s" % (filename))
        except Exception as e:


            cbpi.notify("Failed to load plugin %s " % filename, str(e), type="danger", timeout=None)
            cbpi.app.logger.error(e)

def loadPlugins():
    for filename in os.listdir("./modules/plugins"):
        if os.path.isdir("./modules/plugins/" + filename) is False:
            continue
        try:
            modules[filename] = import_module("modules.plugins.%s" % (filename))
        except Exception as e:
            cbpi.notify("Failed to load plugin %s " % filename, str(e), type="danger", timeout=None)
            cbpi.app.logger.error(e)

#@cbpi.initalizer(order=1)
def initPlugins():
    loadCorePlugins()
    loadPlugins()

@cbpi.initalizer(order=2)
def init(cbpi):

    cbpi.app.register_blueprint(blueprint, url_prefix='/api/editor')
