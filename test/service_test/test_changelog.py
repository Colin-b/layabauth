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
                """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Release note 1.
- Release note 2.

### Added
- Enhancement 1
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2

### Fixed
- Bug fix 1
    - sub bug 1
    - sub bug 2
- Bug fix 2

### Security
- Known issue 1
- Known issue 2

### Deprecated
- Deprecated feature 1
- Future removal 2

### Removed
- Deprecated feature 2
- Future removal 1

## [1.1.0] - 2018-05-31
### Changed
- Enhancement 1 (1.1.0)
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2 (1.1.0)

## [1.0.1] - 2018-05-31
### Fixed
- Bug fix 1 (1.0.1)
    - sub bug 1
    - sub bug 2
- Bug fix 2 (1.0.1)

## [1.0.0] - 2017-04-10
### Deprecated
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
                    "changed": [
                        "- Enhancement 1 (1.1.0)",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2 (1.1.0)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.1.0",
                },
                {
                    "fixed": [
                        "- Bug fix 1 (1.0.1)",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2 (1.0.1)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.0.1",
                },
                {
                    "deprecated": [
                        "- Known issue 1 (1.0.0)",
                        "- Known issue 2 (1.0.0)",
                    ],
                    "release_date": "2017-04-10",
                    "version": "1.0.0",
                },
            ],
        )


class MonitoringWithChangelogWithVersionsAndNoAddedTest(JSONTestCase):
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
                """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Release note 1.
- Release note 2.

### Fixed
- Bug fix 1
    - sub bug 1
    - sub bug 2
- Bug fix 2

### Security
- Known issue 1
- Known issue 2

### Deprecated
- Deprecated feature 1
- Future removal 2

### Removed
- Deprecated feature 2
- Future removal 1

## [1.1.0] - 2018-05-31
### Changed
- Enhancement 1 (1.1.0)
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2 (1.1.0)

## [1.0.1] - 2018-05-31
### Fixed
- Bug fix 1 (1.0.1)
    - sub bug 1
    - sub bug 2
- Bug fix 2 (1.0.1)

## [1.0.0] - 2017-04-10
### Deprecated
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

    def test_changelog_with_versions_and_no_added(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(
            response,
            [
                {
                    "changed": [
                        "- Enhancement 1 (1.1.0)",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2 (1.1.0)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.1.0",
                },
                {
                    "fixed": [
                        "- Bug fix 1 (1.0.1)",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2 (1.0.1)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.0.1",
                },
                {
                    "deprecated": [
                        "- Known issue 1 (1.0.0)",
                        "- Known issue 2 (1.0.0)",
                    ],
                    "release_date": "2017-04-10",
                    "version": "1.0.0",
                },
            ],
        )


class MonitoringWithChangelogWithVersionsAndNoChangedTest(JSONTestCase):
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
                """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Enhancement 1
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2

### Fixed
- Bug fix 1
    - sub bug 1
    - sub bug 2
- Bug fix 2

### Security
- Known issue 1
- Known issue 2

### Deprecated
- Deprecated feature 1
- Future removal 2

### Removed
- Deprecated feature 2
- Future removal 1

## [1.1.0] - 2018-05-31

## [1.0.1] - 2018-05-31
### Fixed
- Bug fix 1 (1.0.1)
    - sub bug 1
    - sub bug 2
- Bug fix 2 (1.0.1)

## [1.0.0] - 2017-04-10
### Deprecated
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

    def test_changelog_with_versions_and_no_changed(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(
            response,
            [
                {"release_date": "2018-05-31", "version": "1.1.0"},
                {
                    "fixed": [
                        "- Bug fix 1 (1.0.1)",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2 (1.0.1)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.0.1",
                },
                {
                    "deprecated": [
                        "- Known issue 1 (1.0.0)",
                        "- Known issue 2 (1.0.0)",
                    ],
                    "release_date": "2017-04-10",
                    "version": "1.0.0",
                },
            ],
        )


class MonitoringWithChangelogWithVersionsAndNoDeprecatedTest(JSONTestCase):
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
                """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Release note 1.
- Release note 2.

### Added
- Enhancement 1
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2

### Fixed
- Bug fix 1
    - sub bug 1
    - sub bug 2
- Bug fix 2

### Security
- Known issue 1
- Known issue 2

### Removed
- Deprecated feature 2
- Future removal 1

## [1.1.0] - 2018-05-31
### Changed
- Enhancement 1 (1.1.0)
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2 (1.1.0)

## [1.0.1] - 2018-05-31
### Fixed
- Bug fix 1 (1.0.1)
    - sub bug 1
    - sub bug 2
- Bug fix 2 (1.0.1)

## [1.0.0] - 2017-04-10
"""
            )

        flask_restplus_common.add_monitoring_namespace(api, pass_details)
        return app

    def tearDown(self):
        if os.path.exists(self.changelog_file_path):
            os.remove(self.changelog_file_path)
        super().tearDown()

    def test_changelog_with_versions_and_no_deprecated(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(
            response,
            [
                {
                    "changed": [
                        "- Enhancement 1 (1.1.0)",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2 (1.1.0)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.1.0",
                },
                {
                    "fixed": [
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


class MonitoringWithChangelogWithVersionsAndNoRemovedTest(JSONTestCase):
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
                """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Release note 1.
- Release note 2.

### Added
- Enhancement 1
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2

### Fixed
- Bug fix 1
    - sub bug 1
    - sub bug 2
- Bug fix 2

### Security
- Known issue 1
- Known issue 2

### Deprecated
- Deprecated feature 1
- Future removal 2

## [1.1.0] - 2018-05-31
### Changed
- Enhancement 1 (1.1.0)
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2 (1.1.0)

## [1.0.1] - 2018-05-31
### Fixed
- Bug fix 1 (1.0.1)
    - sub bug 1
    - sub bug 2
- Bug fix 2 (1.0.1)

## [1.0.0] - 2017-04-10
### Deprecated
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

    def test_changelog_with_versions_and_no_removed(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(
            response,
            [
                {
                    "changed": [
                        "- Enhancement 1 (1.1.0)",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2 (1.1.0)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.1.0",
                },
                {
                    "fixed": [
                        "- Bug fix 1 (1.0.1)",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2 (1.0.1)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.0.1",
                },
                {
                    "deprecated": [
                        "- Known issue 1 (1.0.0)",
                        "- Known issue 2 (1.0.0)",
                    ],
                    "release_date": "2017-04-10",
                    "version": "1.0.0",
                },
            ],
        )


class MonitoringWithChangelogWithVersionsAndNoFixedTest(JSONTestCase):
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
                """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Release note 1.
- Release note 2.

### Added
- Enhancement 1
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2

### Fixed
- Bug fix 1
    - sub bug 1
    - sub bug 2
- Bug fix 2

### Security
- Known issue 1
- Known issue 2

### Deprecated
- Deprecated feature 1
- Future removal 2

### Removed
- Deprecated feature 2
- Future removal 1

## [1.1.0] - 2018-05-31
### Changed
- Enhancement 1 (1.1.0)
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2 (1.1.0)

## [1.0.1] - 2018-05-31
### Fixed
- Bug fix 1 (1.0.1)
    - sub bug 1
    - sub bug 2
- Bug fix 2 (1.0.1)

## [1.0.0] - 2017-04-10
### Deprecated
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

    def test_changelog_with_versions_and_no_fixed(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(
            response,
            [
                {
                    "changed": [
                        "- Enhancement 1 (1.1.0)",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2 (1.1.0)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.1.0",
                },
                {
                    "fixed": [
                        "- Bug fix 1 (1.0.1)",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2 (1.0.1)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.0.1",
                },
                {
                    "deprecated": [
                        "- Known issue 1 (1.0.0)",
                        "- Known issue 2 (1.0.0)",
                    ],
                    "release_date": "2017-04-10",
                    "version": "1.0.0",
                },
            ],
        )


class MonitoringWithChangelogWithVersionsAndNoSecurityTest(JSONTestCase):
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
                """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Release note 1.
- Release note 2.

### Added
- Enhancement 1
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2

### Fixed
- Bug fix 1
    - sub bug 1
    - sub bug 2
- Bug fix 2

### Security
- Known issue 1
- Known issue 2

### Deprecated
- Deprecated feature 1
- Future removal 2

### Removed
- Deprecated feature 2
- Future removal 1

## [1.1.0] - 2018-05-31
### Changed
- Enhancement 1 (1.1.0)
    - sub enhancement 1
    - sub enhancement 2
- Enhancement 2 (1.1.0)

## [1.0.1] - 2018-05-31
### Fixed
- Bug fix 1 (1.0.1)
    - sub bug 1
    - sub bug 2
- Bug fix 2 (1.0.1)

## [1.0.0] - 2017-04-10
### Deprecated
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

    def test_changelog_with_versions_and_no_security(self):
        response = self.client.get("/changelog")
        self.assert_200(response)
        self.assert_json(
            response,
            [
                {
                    "changed": [
                        "- Enhancement 1 (1.1.0)",
                        "- sub enhancement 1",
                        "- sub enhancement 2",
                        "- Enhancement 2 (1.1.0)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.1.0",
                },
                {
                    "fixed": [
                        "- Bug fix 1 (1.0.1)",
                        "- sub bug 1",
                        "- sub bug 2",
                        "- Bug fix 2 (1.0.1)",
                    ],
                    "release_date": "2018-05-31",
                    "version": "1.0.1",
                },
                {
                    "deprecated": [
                        "- Known issue 1 (1.0.0)",
                        "- Known issue 2 (1.0.0)",
                    ],
                    "release_date": "2017-04-10",
                    "version": "1.0.0",
                },
            ],
        )
