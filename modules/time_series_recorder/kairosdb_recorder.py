import logging
import time

import requests
from flask import json

from modules.time_series_recorder.base_recorder import BaseRecorder


class KairosdbRecorder(BaseRecorder):
    kairosdb_ip = "http://192.168.178.20:"
    logger = logging.getLogger(__name__)

    kairosdb_api_status = "/api/v1/health/status"
    kairosdb_api_query = "/api/v1/datapoints/query"

    def __init__(self, port):
        self.kairosdb_url = self.kairosdb_ip + port

    def load_time_series(self, ts_type, ts_id):
        time_series_name = self.compose_time_series_name(ts_type, ts_id)

        data = dict(metrics=[
            {
                "tags": {},
                "name": time_series_name,
                "aggregators": [
                    {
                        "name": "avg",
                        "align_sampling": True,
                        "sampling": {
                            "value": "1",
                            "unit": "minutes"
                        },
                        "align_start_time": True
                    }
                ]
            }
        ],
            cache_time=0,
            start_relative={
                "value": "30",
                "unit": "days"
            })

        response = requests.post(self.kairosdb_url + self.kairosdb_api_query, json.dumps(data))
        if response.ok:
            self.logger.debug("Fetching time series for [{0}] took [{1}]".format(time_series_name, response.elapsed))
            self.logger.debug("Time series for [{0}] is [{1}]".format(time_series_name, response.json()))

            return response.json()["queries"][0]["results"][0]["values"]
        else:
            self.logger.warning("Failed to fetch time series for [{0}]. Response [{1}]", time_series_name, response)

    def check_status(self):
        response = requests.get(self.kairosdb_url + self.kairosdb_api_status)

        return response.json()

    def store_datapoint(self, name, value, tags):
        data = [
            dict(name=name, datapoints=[
                [int(round(time.time() * 1000)), value]
            ], tags={
                "cbpi": tags
            })
        ]

        response = requests.post(self.kairosdb_url + "/api/v1/datapoints", json.dumps(data))

    @staticmethod
    def compose_time_series_name(ts_type, ts_id):
        return "{0}_{1}".format(ts_type, ts_id)
