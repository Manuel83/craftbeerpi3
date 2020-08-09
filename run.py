#!/usr/bin/env python3
"""
cbpi runner
"""


from modules import socketio, app, cbpi

try:
    PORT = int(cbpi.get_config_parameter('port', '5000'))
except ValueError:
    PORT = 5000

socketio.run(app, host='0.0.0.0', port=PORT)
