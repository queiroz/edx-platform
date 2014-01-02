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
    Tests that assume the user is logged in to a unique account.
    We use the auto_auth workflow for this.
    """

    @property
    def page_object_classes(self):
        return []

    @property
    def fixtures(self):
        pass

    def setUp(self):
        """
        Each test begins after creating a user.
        """
        super(StudioLoggedInTest, self).setUp()
        self._login()

    def _login(self):
        """
        Use the auto-auth workflow to create the account and log in.
        Grab the sessionid so future request will use the credentials.
        """
        self.username = 'test_{}'.format(uuid4().hex[:8])
        self.email = '{0}@example.com'.format(self.username)
        self.password = 'password'

        method = 'get'
        path = '/auto_auth?username={}&email={}&password={}'.format(
            self.username, self.email, self.password
        )
        url = '{}{}'.format('http://localhost:8001', path)

        resp = requests.request(method, url)

        cookies = requests.utils.dict_from_cookiejar(resp.cookies)
        self.sessionid = cookies.get('sessionid', '')
        self.csrftoken = cookies.get('csrftoken', 'foo')


class StudioWithCourseTest(StudioLoggedInTest):
    """
    Tests that assume the user is logged in to a unique account
    and is registered for a course.
    """

    @property
    def page_object_classes(self):
        return [DashboardPage]

    @property
    def fixtures(self):
        """
        Create a user account so we can log in.
        The user account is automatically registered for a course.
        """
        pass

    def setUp(self):
        """
        Each test begins after creating a course and navigating
        to the dashboard page.
        """
        super(StudioWithCourseTest, self).setUp()
        self._create_course()

    def _create_course(self):
        """
        Create a Course
        """
        method = 'post'
        path = '/course'
        headers = {
            'content-type': 'application/json',
            'X-CSRFToken': self.csrftoken,
            'accept': 'application/json'
        }
        cookies = dict(csrftoken=self.csrftoken, sessionid=self.sessionid)
        course_num = '{}'.format(uuid4().hex[:4])
        data = {"org":"OrgX","number":course_num,"display_name":"Test Course","run":"2014"}
        url = '{}{}'.format('http://localhost:8001', path)

        from nose.tools import set_trace; set_trace()

        resp = requests.request(method, url, data=json.dumps(data), headers=headers, cookies=cookies)

        self.ui.visit('studio.dashboard')

        print 'ok'
        print 'done'

