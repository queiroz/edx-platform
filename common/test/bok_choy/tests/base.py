"""
Helpful base test case classes for testing the LMS.
"""

from bok_choy.web_app_test import WebAppTest
from .fixtures import UserFixture
from edxapp_pages.studio.login import LoginPage
from edxapp_pages.studio.index import DashboardPage
from uuid import uuid4

class StudioLoggedInTest(WebAppTest):
    """
    Tests that assume the user is logged in to a unique account
    and is registered for a course.
    """

    # Subclasses override these to register the user for a course.
    # If not provided, then skip registration.
    REGISTER_COURSE_ID = None
    REGISTER_COURSE_TITLE = None

    @property
    def page_object_classes(self):
        return [LoginPage, DashboardPage]

    @property
    def fixtures(self):
        """
        Create a user account so we can log in.
        The user account is automatically registered for a course.
        """
        self.username = 'test_{}'.format(uuid4().hex[:8])
        self.email = '{0}@example.com'.format(self.username)
        self.password = 'password'

        return [UserFixture(self.username, self.email, self.password, course=self.REGISTER_COURSE_ID)]

    def setUp(self):
        """
        Each test begins after creating a user.
        """
        super(StudioLoggedInTest, self).setUp()
        self._login()

    def _login(self):
        """
        Log in as the test user, which will navigate to the dashboard.
        """
        self.ui.visit('studio.login')
        self.ui['studio.login'].login(self.email, self.password)
        self.ui.wait_for_page('studio.dashboard')
