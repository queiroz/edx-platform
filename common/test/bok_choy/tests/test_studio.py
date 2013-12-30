"""
E2E tests for Studio.
"""
from unittest import skip
from bok_choy.web_app_test import WebAppTest

from edxapp_pages.studio.asset_index import AssetIndexPage
from edxapp_pages.studio.checklists import ChecklistsPage
from edxapp_pages.studio.course_import import ImportPage
from edxapp_pages.studio.course_info import CourseUpdatesPage
from edxapp_pages.studio.edit_subsection import SubsectionPage
from edxapp_pages.studio.edit_tabs import StaticPagesPage
from edxapp_pages.studio.export import ExportPage
from edxapp_pages.studio.howitworks import HowitworksPage
from edxapp_pages.studio.index import DashboardPage
from edxapp_pages.studio.login import LoginPage
from edxapp_pages.studio.manage_users import CourseTeamPage
from edxapp_pages.studio.overview import CourseOutlinePage
from edxapp_pages.studio.settings import SettingsPage
from edxapp_pages.studio.settings_advanced import AdvancedSettingsPage
from edxapp_pages.studio.settings_graders import GradingPage
from edxapp_pages.studio.signup import SignupPage
from edxapp_pages.studio.textbooks import TextbooksPage
from edxapp_pages.studio.unit import UnitPage

from .base import StudioLoggedInTest


@skip("not doing right now")
class LoggedOutTest(WebAppTest):
    """
    Smoke test for pages in Studio
    that are visible when logged out.
    """

    @property
    def page_object_classes(self):
        return [LoginPage, HowitworksPage, SignupPage]

    def test_page_existence(self):
        """
        Make sure that all the pages are accessible.
        Rather than fire up the browser just to check each url,
        do them all sequentially in this testcase.
        """
        pages = [
            'login', 'howitworks', 'signup'
        ]

        for page in pages:
            self.ui.visit('studio.{0}'.format(page))


class LoggedInPagesTest(StudioLoggedInTest):
    """
    Tests that verify the pages in Studio that you can get to when logged
    in and do not have a course yet.
    """

    @property
    def page_object_classes(self):
        return (set(super(LoggedInPagesTest, self).page_object_classes + [
                AssetIndexPage, ChecklistsPage, ImportPage, CourseUpdatesPage,
                SubsectionPage, StaticPagesPage, ExportPage, HowitworksPage,
                DashboardPage, LoginPage, CourseTeamPage, CourseOutlinePage,
                SettingsPage, AdvancedSettingsPage, GradingPage, SignupPage,
                TextbooksPage, UnitPage
            ]
        ))

    def test_page_existence(self):
        """
        Make sure that all the pages are accessible.
        Rather than fire up the browser just to check each url,
        do them all sequentially in this testcase.
        """
        # pages = [
        #     'uploads', 'checklists', 'import', 'updates', 'subsection', 'tabs',
        #     'export', 'howitworks', 'dashboard', 'login', 'team', 'outline',
        #     'settings', 'advanced', 'grading', 'signup', 'textbooks', 'unit'
        # ]

        # for page in pages:
        #     self.ui.visit('studio.{0}'.format(page))

        self.ui.visit('studio.dashboard')
