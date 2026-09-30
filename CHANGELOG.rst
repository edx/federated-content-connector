Change Log
==========

..
   All enhancements and patches to federated_content_connector will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
----------

1.8.0 - 2026-09-29
------------------
* Added Python 3.12 support (libraries keep both 3.11 and 3.12): tox/CI now run the full
  ``py{311,312}-django{42,52}`` matrix, the weekly requirements-upgrade workflow now
  compiles with Python 3.12, ``pypi-publish.yml`` now builds/releases on 3.12 (previously
  3.8, no longer installable under the new ``python_requires``), and ``setup.py`` declares
  ``python_requires = >=3.11`` with 3.11/3.12 classifiers.
* Regenerated ``requirements/*.txt`` from scratch with Python 3.12 (``make upgrade``).
  ``code-annotations<3.0.0`` held back in ``requirements/constraints.txt`` (3.0.0 requires
  Python >=3.12, which would break the 3.11 leg of the matrix).
* Declared ``pytz`` as an explicit dependency in ``requirements/base.in``. It was only ever
  an undeclared transitive dependency (via old Django/celery pins) despite
  ``filters/pipeline.py`` importing it directly; the regenerated pins no longer pull it in
  transitively, which would otherwise have broken that module at import time.
* Regenerated ``pylintrc``/``.editorconfig`` via ``edx_lint update`` (5.3.4 -> 6.2.0). This
  was required, not just a refresh: pylint was crashing on ``models.py`` because edx-lint
  6.2.0 added a new PII-annotation checker (flags ``.. no_pii:``-annotated models that still
  contain PII-looking fields) that requires a ``pii-terms`` pylintrc setting with no
  default; this repo's two ``.. no_pii:`` models were tripping over the missing config.
* Fixed a real bug in a test mock (``management/commands/tests/test_utils.py``): a new
  pylint 4.0 check (``possibly-used-before-assignment``) caught ``side_effect_func``
  referencing ``response_type`` when neither of its ``if``/``elif`` branches matched;
  added an explicit ``else: raise ValueError(...)``.
* ``docs/conf.py``: Python intersphinx mapping -> 3.12.

1.7.1
------------------
* Added Django 4.2 and 5.2 tox and CI support on Python 3.11.

1.7.0
-----
* Adds a `external_identifier` field to the `CourseDetails` model with a default value of an empty string

1.6.0
-----
* feat: request restricted runs when importing course run data

1.5.2
-----
* fix: gets custom course URL from DB if possible

1.5.1 – 2024-07-25
------------------
* Update release notes

1.5.0 – 2024-07-25
------------------
* Adds a `course_key` field to the `CourseDetails` model with a default value of an empty string

1.4.4 – 2024-02-14
------------------
* No longer rely on `additional_metadata` field to extract metadata such as start, end, and enroll by dates for external courses. Instead, pull directly from the course runs metadata instead.

1.4.3 – 2023-09-27
------------------
* Improvements in `import_course_runs_metadata` and `refresh_course_runs_metadata`

1.4.2 – 2023-09-26
------------------
* Refresh client token for requests

1.4.1 – 2023-09-13
------------------
* Remove inner function from `get_response_from_api`

1.4.0 – 2023-09-12
------------------
* Refactor to fetch course data using course uuid

1.3.2 – 2023-09-04
------------------
* add `include_hidden_course_runs` query param to fetch hidden courseruns
* add retry decorator to handle exceptions during calls to `/courses` api

1.3.1 – 2023-08-28
------------------
* fix: resumeUrl for exec-ed courses in B2C dashboard

1.3.0 – 2023-08-18
------------------
* feat: hook to modify courserun data for B2C dashboard

1.2.1 – 2023-08-03
------------------
* feat: hook for modify course enrollment data

1.2.0 – 2023-07-18
------------------
* Refactor `import_course_runs_metadata` command to import all courseruns

1.1.0 – 2023-06-21
------------------
* Management command to refresh CourseDetails data

1.0.3 – 2023-06-15
------------------
* backfill all data

1.0.2 – 2023-06-15
------------------
* Handle empty courserun seats.
* Add limit query param in api call

1.0.1 – 2023-06-14
------------------
* Update courserun seat sorting logic.

1.0.0 – 2023-06-06
------------------
* Fetch course metadata from discovery and store.

0.2.1 – 2023-06-5
------------------
* Fixed issue with product source data type

0.2.0 – 2023-05-31
------------------
* Added support for stage and prod landing pages via settings

0.1.1 – 2023-05-26
------------------
* Fixes for PyPI description markup.

0.1.0 – 2023-05-26
------------------
* Basic skeleton of the app.
* CreateCustomUrlForCourseStep pipeline.
* First release on PyPI.
