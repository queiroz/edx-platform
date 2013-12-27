"""
Tests authz.py
"""
import mock

from django.test import TestCase
from django.contrib.auth.models import User
from xmodule.modulestore import Location
from django.core.exceptions import PermissionDenied

from student.roles import CourseInstructorRole, CourseStaffRole, CourseCreatorRole
from student.tests.factories import AdminFactory


class CreatorGroupTest(TestCase):
    """
    Tests for the course creator group.
    """

    def setUp(self):
        """ Test case setup """
        self.user = User.objects.create_user('testuser', 'test+courses@edx.org', 'foo')
        self.admin = User.objects.create_user('Mark', 'admin+courses@edx.org', 'foo')
        self.admin.is_staff = True

    def test_creator_group_not_enabled(self):
        """
        Tests that CourseCreatorRole().has_user always returns True if ENABLE_CREATOR_GROUP
        and DISABLE_COURSE_CREATION are both not turned on.
        """
        self.assertTrue(CourseCreatorRole().has_user(self.user))

    def test_creator_group_enabled_but_empty(self):
        """ Tests creator group feature on, but group empty. """
        with mock.patch.dict('django.conf.settings.FEATURES', {"ENABLE_CREATOR_GROUP": True}):
            self.assertFalse(CourseCreatorRole().has_user(self.user))

            # Make user staff. This will cause CourseCreatorRole().has_user to return True.
            self.user.is_staff = True
            self.assertTrue(CourseCreatorRole().has_user(self.user))

    def test_creator_group_enabled_nonempty(self):
        """ Tests creator group feature on, user added. """
        with mock.patch.dict('django.conf.settings.FEATURES', {"ENABLE_CREATOR_GROUP": True}):
            CourseCreatorRole().add_users(self.admin, self.user)
            self.assertTrue(CourseCreatorRole().has_user(self.user))

            # check that a user who has not been added to the group still returns false
            user_not_added = User.objects.create_user('testuser2', 'test+courses2@edx.org', 'foo2')
            self.assertFalse(CourseCreatorRole().has_user(user_not_added))

            # remove first user from the group and verify that CourseCreatorRole().has_user now returns false
            CourseCreatorRole().remove_users(self.admin, self.user)
            self.assertFalse(CourseCreatorRole().has_user(self.user))

    def test_course_creation_disabled(self):
        """ Tests that the COURSE_CREATION_DISABLED flag overrides course creator group settings. """
        with mock.patch.dict('django.conf.settings.FEATURES',
                             {'DISABLE_COURSE_CREATION': True, "ENABLE_CREATOR_GROUP": True}):
            # Add user to creator group.
            CourseCreatorRole().add_users(self.admin, self.user)

            # DISABLE_COURSE_CREATION overrides (user is not marked as staff).
            self.assertFalse(CourseCreatorRole().has_user(self.user))

            # Mark as staff. Now CourseCreatorRole().has_user returns true.
            self.user.is_staff = True
            self.assertTrue(CourseCreatorRole().has_user(self.user))

            # Remove user from creator group. CourseCreatorRole().has_user still returns true because is_staff=True
            CourseCreatorRole().remove_users(self.admin, self.user)
            self.assertTrue(CourseCreatorRole().has_user(self.user))

    def test_add_user_to_group_requires_staff_access(self):
        with self.assertRaises(PermissionDenied):
            self.admin.is_staff = False
            CourseCreatorRole().add_users(self.admin, self.user)

        with self.assertRaises(PermissionDenied):
            CourseCreatorRole().add_users(self.user, self.user)

    def test_add_user_to_group_requires_active(self):
        with self.assertRaises(PermissionDenied):
            self.admin.is_active = False
            CourseCreatorRole().add_users(self.admin, self.user)

    def test_add_user_to_group_requires_authenticated(self):
        with self.assertRaises(PermissionDenied):
            self.admin.is_authenticated = False
            CourseCreatorRole().add_users(self.admin, self.user)

    def test_remove_user_from_group_requires_staff_access(self):
        with self.assertRaises(PermissionDenied):
            self.admin.is_staff = False
            CourseCreatorRole().remove_users(self.admin, self.user)

    def test_remove_user_from_group_requires_active(self):
        with self.assertRaises(PermissionDenied):
            self.admin.is_active = False
            CourseCreatorRole().remove_users(self.admin, self.user)

    def test_remove_user_from_group_requires_authenticated(self):
        with self.assertRaises(PermissionDenied):
            self.admin.is_authenticated = False
            CourseCreatorRole().remove_users(self.admin, self.user)


class CourseGroupTest(TestCase):
    """
    Tests for instructor and staff groups for a particular course.
    """

    def setUp(self):
        """ Test case setup """
        self.global_admin = AdminFactory()
        self.creator = User.objects.create_user('testcreator', 'testcreator+courses@edx.org', 'foo')
        self.staff = User.objects.create_user('teststaff', 'teststaff+courses@edx.org', 'foo')
        self.location = Location('i4x', 'mitX', '101', 'course', 'test')

    def test_add_user_to_course_group(self):
        """
        Tests adding user to course group (happy path).
        """
        # Create groups for a new course (and assign instructor role to the creator).
        self.assertFalse(CourseInstructorRole(self.location).has_user(self.creator))
        CourseInstructorRole(self.location).add_users(self.global_admin, self.creator)
        CourseStaffRole(self.location).add_users(self.global_admin, self.creator)
        self.assertTrue(CourseInstructorRole(self.location).has_user(self.creator))

        # Add another user to the staff role.
        self.assertFalse(CourseStaffRole(self.location).has_user(self.staff))
        CourseStaffRole(self.location).add_users(self.creator, self.staff)
        self.assertTrue(CourseStaffRole(self.location).has_user(self.staff))

    def test_add_user_to_course_group_permission_denied(self):
        """
        Verifies PermissionDenied if caller of add_user_to_course_group is not instructor role.
        """
        CourseInstructorRole(self.location).add_users(self.global_admin, self.creator)
        CourseStaffRole(self.location).add_users(self.global_admin, self.creator)
        with self.assertRaises(PermissionDenied):
            CourseStaffRole(self.location).add_users(self.staff, self.staff)

    def test_remove_user_from_course_group(self):
        """
        Tests removing user from course group (happy path).
        """
        CourseInstructorRole(self.location).add_users(self.global_admin, self.creator)
        CourseStaffRole(self.location).add_users(self.global_admin, self.creator)

        CourseStaffRole(self.location).add_users(self.creator, self.staff)
        self.assertTrue(CourseStaffRole(self.location).has_user(self.staff))

        CourseStaffRole(self.location).remove_users(self.creator, self.staff)
        self.assertFalse(CourseStaffRole(self.location).has_user(self.staff))

        CourseInstructorRole(self.location).remove_users(self.creator, self.creator)
        self.assertFalse(CourseInstructorRole(self.location).has_user(self.creator))

    def test_remove_user_from_course_group_permission_denied(self):
        """
        Verifies PermissionDenied if caller of remove_user_from_course_group is not instructor role.
        """
        CourseInstructorRole(self.location).add_users(self.global_admin, self.creator)
        another_staff = User.objects.create_user('another', 'teststaff+anothercourses@edx.org', 'foo')
        CourseStaffRole(self.location).add_users(self.global_admin, self.creator, self.staff, another_staff)
        with self.assertRaises(PermissionDenied):
            CourseStaffRole(self.location).remove_users(self.staff, another_staff)
