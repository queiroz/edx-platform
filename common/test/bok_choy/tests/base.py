"""
Helpful base test case classes for testing the LMS.
"""

from bok_choy.web_app_test import WebAppTest
from .fixtures import UserFixture
from edxapp_pages.studio.login import LoginPage
from edxapp_pages.studio.index import DashboardPage
from uuid import uuid4
import requests
import os
import re
import json

class StudioLoggedInTest(WebAppTest):
    """
    Tests that assume the user is logged in to a unique account
    and is registered for a course.
    """

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

        return [UserFixture(self.username, self.email, self.password)]

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


class StudioWithCourseTest(WebAppTest):
    """
    Tests that assume the user is logged in to a unique account
    and is registered for a course.
    """

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

        return [UserFixture(self.username, self.email, self.password)]

    def setUp(self):
        """
        Each test begins after creating a user.
        """
        super(StudioWithCourseTest, self).setUp()
        self._login()
        self._create_course()

    def _login(self):
        """
        Log in as the test user, which will navigate to the dashboard.
        """
        self.ui.visit('studio.login')
        self.ui['studio.login'].login(self.email, self.password)
        self.ui.wait_for_page('studio.dashboard')
        cookies = self.ui._browser.cookies.all()
        self.csrftoken = ''
        for cookie in cookies:
            if cookie['name'] == 'csrftoken':
                self.csrftoken = cookie['value']
                break

    def _create_course(self):
        """
        Create a Course
        """
        _csrf_token = 'foo'
        # method = 'post'
        # path = '/login_post'
        # url = '{}{}'.format('http://localhost:8031', path)
        # headers = {'content-type': 'application/json', 'X-CSRFToken': _csrf_token}
        # data = {"email": self.email, "password": self.password, "honor_code": "true"}
        # cookies = dict(csrftoken=_csrf_token)

        # resp = requests.request(
        #     method, url, data=json.dumps(data), headers=headers, cookies=cookies
        # )

        method = 'post'
        path = '/course'
        headers = {'content-type': 'application/json', 'X-CSRFToken': _csrf_token}
        cookies = dict(csrftoken=_csrf_token)
        course_num = '{}'.format(uuid4().hex[:4])
        data = {"org":"OrgX","number":course_num,"display_name":"Test Course","run":"2014"}
        url = '{}{}'.format('http://localhost:8031', path)

        from nose.tools import set_trace; set_trace()
        resp = requests.request(method, url, data=json.dumps(data), headers=headers, cookies=cookies)

        print 'ok'
        print 'done'

