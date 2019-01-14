import datetime
import json

import pandas as pd
from flask import Flask
from flask_testing import TestCase
from pycommon_test import mock_now

from pycommon_server.pandas_responses import dataframe_as_response


class HttpUtilTest(TestCase):

    def setUp(self):
        mock_now()

    def create_app(self):
        app = Flask(__name__)
        app.testing = True
        return app

    def test_dataframe_200(self):
        data = [{'key1': 'row11', 'key2': 'row12'}, {'key1': 'row21', 'key2': datetime.datetime.now()}]
        expected_data = [{'key1': 'row11', 'key2': 'row12'}, {'key1': 'row21', 'key2': '2018-10-11T15:05:05.663Z'}]
        df = pd.DataFrame.from_dict(data)
        response = dataframe_as_response(df)
        self.assertEqual(expected_data, json.loads(response.data))
        self.assertEqual('application/json', response.headers.get('Content-type'))
        self.assert200(response)
