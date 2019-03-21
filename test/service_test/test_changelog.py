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
        self.assert_500(response)
        self.assert_text(response, "No changelog can be found. Please contact support.")


class MonitoringWithChangelogWithoutVersionTest(JSONTestCase):
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

    def test_changelog_without_versions(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(response, [])


class MonitoringWithChangelogWithVersionsAndAllCategoriesTest(JSONTestCase):
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
            file.write(
                """# Test Changelog #

List all changes in various categories:
* Release notes: Contains all worth noting changes (breaking changes mainly)
* Enhancements
* Bug fixes
* Known issues

## Version 2.0.0 (next) ##

### Release notes ###

- Release note 1.
- Release note 2.

### Enhancements ###

- Enhancement 1
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2

### Bug fixes ###

- Bug fix 1
    - sub bug 1
    - sub bug 2
- Bug fix 2

### Known issues ###

- Known issue 1
- Known issue 2

## Version 1.1.0 (2018-05-31) ##

### Enhancements ###

- Enhancement 1 (1.1.0)
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2 (1.1.0)

## Version 1.0.1 (2018-05-31) ##

### Bug fixes ###

- Bug fix 1 (1.0.1)
    - sub bug 1
    - sub bug 2
- Bug fix 2 (1.0.1)

## Version 1.0.0 (2017-04-10) ##

### Known issues ###

- Known issue 1 (1.0.0)
- Known issue 2 (1.0.0)
"""
            )

        flask_restplus_common.add_monitoring_namespace(api, pass_details)
        return app

    def tearDown(self):
        if os.path.exists(self.changelog_file_path):
            os.remove(self.changelog_file_path)
        super().tearDown()

    def test_changelog_with_versions_and_all_categories(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(
            response,
            [
                {
                    "bug_fixes": [
                        "- Bug fix 1",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2",
                    ],
                    "enhancements": [
                        "- Enhancement 1",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2",
                    ],
                    "known_issues": ["- Known issue 1", "- Known issue 2"],
                    "release_date": "next",
                    "release_notes": ["- Release note 1.", "- Release note 2."],
                    "version": "2.0.0",
                },
                {
                    "enhancements": [
                        "- Enhancement 1 (1.1.0)",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2 (1.1.0)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.1.0",
                },
                {
                    "bug_fixes": [
                        "- Bug fix 1 (1.0.1)",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2 (1.0.1)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.0.1",
                },
                {
                    "known_issues": [
                        "- Known issue 1 (1.0.0)",
                        "- Known issue 2 (1.0.0)",
                    ],
                    "release_date": "2017-04-10",
                    "version": "1.0.0",
                },
            ],
        )


class MonitoringWithChangelogWithVersionsAndNoReleaseNotesTest(JSONTestCase):
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
            file.write(
                """# Test Changelog #

List all changes in various categories:
* Release notes: Contains all worth noting changes (breaking changes mainly)
* Enhancements
* Bug fixes
* Known issues

## Version 2.0.0 (next) ##

### Enhancements ###

- Enhancement 1
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2

### Bug fixes ###

- Bug fix 1
    - sub bug 1
    - sub bug 2
- Bug fix 2

### Known issues ###

- Known issue 1
- Known issue 2

## Version 1.1.0 (2018-05-31) ##

### Enhancements ###

- Enhancement 1 (1.1.0)
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2 (1.1.0)

## Version 1.0.1 (2018-05-31) ##

### Bug fixes ###

- Bug fix 1 (1.0.1)
    - sub bug 1
    - sub bug 2
- Bug fix 2 (1.0.1)

## Version 1.0.0 (2017-04-10) ##

### Known issues ###

- Known issue 1 (1.0.0)
- Known issue 2 (1.0.0)
"""
            )

        flask_restplus_common.add_monitoring_namespace(api, pass_details)
        return app

    def tearDown(self):
        if os.path.exists(self.changelog_file_path):
            os.remove(self.changelog_file_path)
        super().tearDown()

    def test_changelog_with_versions_and_no_release_notes(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(
            response,
            [
                {
                    "bug_fixes": [
                        "- Bug fix 1",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2",
                    ],
                    "enhancements": [
                        "- Enhancement 1",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2",
                    ],
                    "known_issues": ["- Known issue 1", "- Known issue 2"],
                    "release_date": "next",
                    "version": "2.0.0",
                },
                {
                    "enhancements": [
                        "- Enhancement 1 (1.1.0)",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2 (1.1.0)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.1.0",
                },
                {
                    "bug_fixes": [
                        "- Bug fix 1 (1.0.1)",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2 (1.0.1)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.0.1",
                },
                {
                    "known_issues": [
                        "- Known issue 1 (1.0.0)",
                        "- Known issue 2 (1.0.0)",
                    ],
                    "release_date": "2017-04-10",
                    "version": "1.0.0",
                },
            ],
        )


class MonitoringWithChangelogWithVersionsAndNoEnhancementsTest(JSONTestCase):
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
            file.write(
                """# Test Changelog #

List all changes in various categories:
* Release notes: Contains all worth noting changes (breaking changes mainly)
* Enhancements
* Bug fixes
* Known issues

## Version 2.0.0 (next) ##

### Release notes ###

- Release note 1.
- Release note 2.

### Bug fixes ###

- Bug fix 1
    - sub bug 1
    - sub bug 2
- Bug fix 2

### Known issues ###

- Known issue 1
- Known issue 2

## Version 1.1.0 (2018-05-31) ##

## Version 1.0.1 (2018-05-31) ##

### Bug fixes ###

- Bug fix 1 (1.0.1)
    - sub bug 1
    - sub bug 2
- Bug fix 2 (1.0.1)

## Version 1.0.0 (2017-04-10) ##

### Known issues ###

- Known issue 1 (1.0.0)
- Known issue 2 (1.0.0)
"""
            )

        flask_restplus_common.add_monitoring_namespace(api, pass_details)
        return app

    def tearDown(self):
        if os.path.exists(self.changelog_file_path):
            os.remove(self.changelog_file_path)
        super().tearDown()

    def test_changelog_with_versions_and_no_enhancements(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(
            response,
            [
                {
                    "bug_fixes": [
                        "- Bug fix 1",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2",
                    ],
                    "known_issues": ["- Known issue 1", "- Known issue 2"],
                    "release_date": "next",
                    "release_notes": ["- Release note 1.", "- Release note 2."],
                    "version": "2.0.0",
                },
                {"release_date": "2018-05-31", "version": "1.1.0"},
                {
                    "bug_fixes": [
                        "- Bug fix 1 (1.0.1)",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2 (1.0.1)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.0.1",
                },
                {
                    "known_issues": [
                        "- Known issue 1 (1.0.0)",
                        "- Known issue 2 (1.0.0)",
                    ],
                    "release_date": "2017-04-10",
                    "version": "1.0.0",
                },
            ],
        )


class MonitoringWithChangelogWithVersionsAndNoBugFixesTest(JSONTestCase):
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
            file.write(
                """# Test Changelog #

List all changes in various categories:
* Release notes: Contains all worth noting changes (breaking changes mainly)
* Enhancements
* Bug fixes
* Known issues

## Version 2.0.0 (next) ##

### Release notes ###

- Release note 1.
- Release note 2.

### Enhancements ###

- Enhancement 1
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2

### Known issues ###

- Known issue 1
- Known issue 2

## Version 1.1.0 (2018-05-31) ##

### Enhancements ###

- Enhancement 1 (1.1.0)
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2 (1.1.0)

## Version 1.0.1 (2018-05-31) ##

## Version 1.0.0 (2017-04-10) ##

### Known issues ###

- Known issue 1 (1.0.0)
- Known issue 2 (1.0.0)
"""
            )

        flask_restplus_common.add_monitoring_namespace(api, pass_details)
        return app

    def tearDown(self):
        if os.path.exists(self.changelog_file_path):
            os.remove(self.changelog_file_path)
        super().tearDown()

    def test_changelog_with_versions_and_no_bug_fixes(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(
            response,
            [
                {
                    "enhancements": [
                        "- Enhancement 1",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2",
                    ],
                    "known_issues": ["- Known issue 1", "- Known issue 2"],
                    "release_date": "next",
                    "release_notes": ["- Release note 1.", "- Release note 2."],
                    "version": "2.0.0",
                },
                {
                    "enhancements": [
                        "- Enhancement 1 (1.1.0)",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2 (1.1.0)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.1.0",
                },
                {"release_date": "2018-05-31", "version": "1.0.1"},
                {
                    "known_issues": [
                        "- Known issue 1 (1.0.0)",
                        "- Known issue 2 (1.0.0)",
                    ],
                    "release_date": "2017-04-10",
                    "version": "1.0.0",
                },
            ],
        )


class MonitoringWithChangelogWithVersionsAndNoKnownIssuesTest(JSONTestCase):
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
            file.write(
                """# Test Changelog #

List all changes in various categories:
* Release notes: Contains all worth noting changes (breaking changes mainly)
* Enhancements
* Bug fixes
* Known issues

## Version 2.0.0 (next) ##

### Release notes ###

- Release note 1.
- Release note 2.

### Enhancements ###

- Enhancement 1
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2

### Bug fixes ###

- Bug fix 1
    - sub bug 1
    - sub bug 2
- Bug fix 2

## Version 1.1.0 (2018-05-31) ##

### Enhancements ###

- Enhancement 1 (1.1.0)
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2 (1.1.0)

## Version 1.0.1 (2018-05-31) ##

### Bug fixes ###

- Bug fix 1 (1.0.1)
    - sub bug 1
    - sub bug 2
- Bug fix 2 (1.0.1)

## Version 1.0.0 (2017-04-10) ##
"""
            )

        flask_restplus_common.add_monitoring_namespace(api, pass_details)
        return app

    def tearDown(self):
        if os.path.exists(self.changelog_file_path):
            os.remove(self.changelog_file_path)
        super().tearDown()

    def test_changelog_with_versions_and_no_known_issues(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(
            response,
            [
                {
                    "bug_fixes": [
                        "- Bug fix 1",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2",
                    ],
                    "enhancements": [
                        "- Enhancement 1",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2",
                    ],
                    "release_date": "next",
                    "release_notes": ["- Release note 1.", "- Release note 2."],
                    "version": "2.0.0",
                },
                {
                    "enhancements": [
                        "- Enhancement 1 (1.1.0)",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2 (1.1.0)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.1.0",
                },
                {
                    "bug_fixes": [
                        "- Bug fix 1 (1.0.1)",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2 (1.0.1)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.0.1",
                },
                {"release_date": "2017-04-10", "version": "1.0.0"},
            ],
        )
