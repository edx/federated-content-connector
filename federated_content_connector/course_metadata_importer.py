""""Course metadata importer"""

import logging
from urllib.parse import quote_plus

from django.contrib.auth import get_user_model

from federated_content_connector.models import CourseDetails

from common.djangoapps.course_modes.models import CourseMode
from openedx.core.djangoapps.catalog.models import CatalogIntegration
from openedx.core.djangoapps.catalog.utils import get_catalog_api_base_url, get_catalog_api_client
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

EXEC_ED_COURSE_TYPE = "executive-education-2u"
BEST_MODE_ORDER = [
    CourseMode.VERIFIED,
    CourseMode.PROFESSIONAL,
    CourseMode.NO_ID_PROFESSIONAL_MODE,
    CourseMode.UNPAID_EXECUTIVE_EDUCATION,
    CourseMode.AUDIT,
]

logger = logging.getLogger(__name__)
User = get_user_model()  # pylint: disable=invalid-name


class CourseMetadataImporter(object):
    """Import course metadata from discovery"""

    @classmethod
    def get_api_client(cls):
        """Returns discovery api client"""
        catalog_integration = CatalogIntegration.current()
        username = catalog_integration.service_username

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.exception(
                f'Failed to create API client. Service user {username} does not exist.'
            )
            raise

        return get_catalog_api_client(user)

    @classmethod
    def import_courses_metadata(cls, courserun_keys=None):
        """
        Import course metadata for all or specific courses.

        Args:
            courserun_keys (list): list of courserun keys
        """
        client = cls.get_api_client()

        filter_ = None
        if courserun_keys:
            filter_ = {'id__in': courserun_keys}

        # TODO: Which courses we should consider and which courses we should exclude?
        # TODO: What to do with old style course keys?
        all_courserun_locators = CourseOverview.get_all_courses(filter_=filter_).values_list('id', flat=True)
        for courserun_locators in cls.chunks(all_courserun_locators):

            # convert course locator objects to courserun keys
            courserun_keys = map(str, courserun_locators)

            logger.info(f'[COURSE_METADATA_IMPORTER] Importing metadata. Courses: {courserun_keys}')

            course_details = cls.fetch_courses_details(client, courserun_locators, get_catalog_api_base_url())
            processed_courses_details = cls.process_courses_details(courserun_locators, course_details)
            cls.store_courses_details(processed_courses_details)

            logger.info(f'[COURSE_METADATA_IMPORTER] Import completed. Courses: {courserun_keys}')

        if filter_ is None:
            logger.info(f'[COURSE_METADATA_IMPORTER] Course metadata import completed for all courses.')

    @classmethod
    def fetch_courses_details(cls, client, courserun_locators, api_base_url):  # lint-amnesty, pylint: disable=missing-function-docstring
        """
        Fetch the course data from discovery using `/api/v1/courses` endpoint
        """
        course_keys = [cls.construct_course_key(courserun_locator) for courserun_locator in courserun_locators]
        encoded_course_keys = ','.join(map(quote_plus, course_keys))

        logger.info(f'[COURSE_METADATA_IMPORTER] Fetching details from discovery. Courses {course_keys}.')
        api_url = f"{api_base_url}/courses/?keys={encoded_course_keys}"
        response = client.get(api_url)
        response.raise_for_status()
        courses_details = response.json()
        results = courses_details.get('results', [])

        return results

    @classmethod
    def process_courses_details(cls, courserun_locators, courses_details):
        """
        Parse and extract the minimal data that we need.
        """
        courses = {}
        for courserun_locator in courserun_locators:
            course_key = cls.construct_course_key(courserun_locator)
            courserun_key = str(courserun_locator)
            course_metadata = cls.find_attr(courses_details, 'key', course_key)

            course_type = course_metadata.get('course_type') or ''
            product_source = course_metadata.get('product_source') or ''
            if product_source:
                product_source = product_source.get('slug')

            enroll_by = start_date = end_date = None

            if course_type == EXEC_ED_COURSE_TYPE:
                additional_metadata = course_metadata.get('additional_metadata')
                if additional_metadata:
                    enroll_by = additional_metadata.get('registration_deadline')
                    start_date = additional_metadata.get('start_date')
                    end_date = additional_metadata.get('end_date')
            else:
                course_run = cls.find_attr(course_metadata.get('course_runs'), 'key', courserun_key)
                seat = cls.find_best_mode_seat(course_run.get('seats'))
                enroll_by = seat.get('upgrade_deadline')
                start_date = course_run.get('start')
                end_date = course_run.get('end')

            course_data = {
                'course_type': course_type,
                'product_source': product_source,
                'enroll_by': enroll_by,
                'start_date': start_date,
                'end_date': end_date,
            }
            courses[courserun_key] = course_data

        return courses

    @classmethod
    def store_courses_details(cls, courses_details):
        """
        Store courses metadata in database.
        """
        for courserun_key, course_detail in courses_details.items():
            CourseDetails.objects.get_or_create(
                id=courserun_key,
                defaults=course_detail
            )

    @classmethod
    def find_best_mode_seat(cls, seats):
        """
        Find the seat by best course mode
        """
        return sorted(seats, key=lambda x: BEST_MODE_ORDER.index(x['type']))[0]

    @classmethod
    def chunks(cls, keys, chunk_size=50):
        """
        Yield chunks of size `chunk_size`
        """
        for i in range(0, len(keys), chunk_size):
            yield keys[i:i + chunk_size]

    @staticmethod
    def construct_course_key(course_locator):
        """
        Construct course key from course run key.
        """
        # TODO: What to do with old sytle course and course run keys?
        return f'{course_locator.org}+{course_locator.course}'

    @classmethod
    def find_attr(cls, iterable, attr_name, attr_value):
        """
        Find value of an attribute from with in an iterable.
        """
        for item in iterable:
            if item[attr_name] == attr_value:
                return item
