import datetime
import json
from io import BytesIO

import pandas as pd
from flask import Flask
from flask_testing import TestCase
from openpyxl import load_workbook
from pycommon_test import mock_now

from pycommon_server.pandas_responses import dataframe_200, dataframe_as_excel_200


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
        response = dataframe_200(df)
        self.assertEqual(expected_data, json.loads(response.data))
        self.assertEqual('application/json', response.headers.get('Content-type'))
        self.assert200(response)

    def test_dataframe_to_excel_200(self):
        keys = ['key1', 'key2']
        data = [{'key1': 'row11', 'key2': 'row12'}, {'key1': 'row21', 'key2': datetime.datetime.now()}]
        expected_data = [{'key1': 'row11', 'key2': 'row12'},
                         {'key1': 'row21', 'key2': datetime.datetime(2018, 10, 11, 15, 5, 5, 663978)}]
        df = pd.DataFrame.from_dict(data)
        response = dataframe_as_excel_200(df, file_name='test.xlsx', sheet_name='test_sheet')
        self.assertEqual('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         response.headers.get('Content-type'))
        self.assertEqual('attachment; filename=test.xlsx', response.headers.get('Content-Disposition'))
        self.assert200(response)
        wb = load_workbook(filename=BytesIO(response.data), read_only=True)
        ws = wb['test_sheet']
        current_row = 0
        for row in ws.rows:
            current_col = 0
            for cell in row:
                if current_row == 0:
                    ## this is the header
                    self.assertEqual(keys[current_col], cell.value)
                else:
                    self.assertEqual(expected_data[current_row - 1][keys[current_col]], cell.value)
                current_col += 1
            current_row += 1
