import logging
import os
import os.path
from flask import Flask
from flask_restplus import Api
from pycommon_test.service_tester import JSONTestCase

from pycommon_server import flask_restplus_common

logger = logging.getLogger(__name__)


class MonitoringWithoutChangelogTest(JSONTestCase):
    def create_app(self):
        app = Flask(__name__)
        app.testing = True
        api = Api(app, version="3.2.1")

        def pass_details():
            return "pass", {"toto2": {"status": "pass"}}

        flask_restplus_common.add_monitoring_namespace(api, pass_details)
        return app

    def test_changelog_not_found(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_text(response, "No changelog can be found. Please contact support.")


class MonitoringWithChangelogTest(JSONTestCase):
    def create_app(self):
        self.changelog_file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "CHANGELOG.md"
        )

        app = Flask(__name__)
        app.testing = True
        api = Api(app, version="3.2.1")

        def pass_details():
            return "pass", {"toto2": {"status": "pass"}}

        with open(self.changelog_file_path, "wt") as file:
            file.write("This is the changelog content.\n")
            file.write("This is the second line.\n")

        flask_restplus_common.add_monitoring_namespace(api, pass_details)
        return app

    def tearDown(self):
        if os.path.exists(self.changelog_file_path):
            os.remove(self.changelog_file_path)
        super().tearDown()

    def test_changelog_found(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_text(
            response,
            """This is the changelog content.
This is the second line.
""",
        )
