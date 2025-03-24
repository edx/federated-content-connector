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
* Nothing unreleased

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
