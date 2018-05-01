#!/usr/bin/env python

from modules.core.core import *
from modules.core.db_migrate import *
from modules.buzzer import *
from modules.config import *
from modules.login import *
from modules.system import *
from modules.ui import *
from modules.step import *
from modules.kettle import *
from modules.actor import *
from modules.plugin import *
from modules.logs import *
from modules.notification import *
from modules.sensor import *
from modules.recipe_import import *
from modules.fermenter import *
from modules.action import *
from modules.base_plugins.actor import *
from modules.base_plugins.sensor import *
from modules.base_plugins.steps import *
from modules.example_plugins.WebViewJquery import *
from modules.example_plugins.WebViewReactJs import *
from modules.example_plugins.swagger import *
from modules.time_series_recorder import *

cbpi.run()
