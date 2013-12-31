"""
Tests for contentstore/views/user.py.
"""
import json
from .utils import CourseTestCase
from django.contrib.auth.models import User, Group
from student.models import CourseEnrollment
from xmodule.modulestore.django import loc_mapper
from student.roles import CourseStaffRole, CourseInstructorRole


class UsersTestCase(CourseTestCase):
    def setUp(self):
        super(UsersTestCase, self).setUp()
        self.ext_user = User.objects.create_user(
            "joe", "joe@comedycentral.com", "haha")
        self.ext_user.is_active = True
        self.ext_user.is_staff = False
        self.ext_user.save()
        self.inactive_user = User.objects.create_user(
            "carl", "carl@comedycentral.com", "haha")
        self.inactive_user.is_active = False
        self.inactive_user.is_staff = False
        self.inactive_user.save()

        self.location = loc_mapper().translate_location(self.course.location.course_id, self.course.location, False, True)

        self.index_url = self.location.url_reverse('course_team', '')
        self.detail_url = self.location.url_reverse('course_team', self.ext_user.email)
        self.inactive_detail_url = self.location.url_reverse('course_team', self.inactive_user.email)
        self.invalid_detail_url = self.location.url_reverse('course_team', "nonexistent@user.com")
        # pylint: disable=protected-access
        self.staff_groupname = CourseStaffRole(self.course_locator)._group_names[0]
        self.inst_groupname = CourseInstructorRole(self.course_locator)._group_names[0]

    def test_index(self):
        resp = self.client.get(self.index_url, HTTP_ACCEPT='text/html')
        # ext_user is not currently a member of the course team, and so should
        # not show up on the page.
        self.assertNotContains(resp, self.ext_user.email)

    def test_index_member(self):
        group, _ = Group.objects.get_or_create(name=self.staff_groupname)
        self.ext_user.groups.add(group)
        self.ext_user.save()

        resp = self.client.get(self.index_url, HTTP_ACCEPT='text/html')
        self.assertContains(resp, self.ext_user.email)

    def test_detail(self):
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.content)
        self.assertEqual(result["role"], None)
        self.assertTrue(result["active"])

    def test_detail_inactive(self):
        resp = self.client.get(self.inactive_detail_url)
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.content)
        self.assertFalse(result["active"])

    def test_detail_invalid(self):
        resp = self.client.get(self.invalid_detail_url)
        self.assertEqual(resp.status_code, 404)
        result = json.loads(resp.content)
        self.assertIn("error", result)

    def test_detail_post(self):
        resp = self.client.post(
            self.detail_url,
            data={"role": None},
        )
        self.assertEqual(resp.status_code, 204)
        # reload user from DB
        ext_user = User.objects.get(email=self.ext_user.email)
        groups = [g.name for g in ext_user.groups.all()]
        # no content: should not be in any roles
        self.assertNotIn(self.staff_groupname, groups)
        self.assertNotIn(self.inst_groupname, groups)
        self.assert_not_enrolled()

    def test_detail_post_staff(self):
        resp = self.client.post(
            self.detail_url,
            data=json.dumps({"role": "staff"}),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 204)
        # reload user from DB
        ext_user = User.objects.get(email=self.ext_user.email)
        groups = [g.name for g in ext_user.groups.all()]
        self.assertIn(self.staff_groupname, groups)
        self.assertNotIn(self.inst_groupname, groups)
        self.assert_enrolled()

    def test_detail_post_staff_other_inst(self):
        inst_group, _ = Group.objects.get_or_create(name=self.inst_groupname)
        self.user.groups.add(inst_group)
        self.user.save()

        resp = self.client.post(
            self.detail_url,
            data=json.dumps({"role": "staff"}),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 204)
        # reload user from DB
        ext_user = User.objects.get(email=self.ext_user.email)
        groups = [g.name for g in ext_user.groups.all()]
        self.assertIn(self.staff_groupname, groups)
        self.assertNotIn(self.inst_groupname, groups)
        self.assert_enrolled()
        # check that other user is unchanged
        user = User.objects.get(email=self.user.email)
        groups = [g.name for g in user.groups.all()]
        self.assertNotIn(self.staff_groupname, groups)
        self.assertIn(self.inst_groupname, groups)

    def test_detail_post_instructor(self):
        resp = self.client.post(
            self.detail_url,
            data=json.dumps({"role": "instructor"}),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 204)
        # reload user from DB
        ext_user = User.objects.get(email=self.ext_user.email)
        groups = [g.name for g in ext_user.groups.all()]
        self.assertNotIn(self.staff_groupname, groups)
        self.assertIn(self.inst_groupname, groups)
        self.assert_enrolled()

    def test_detail_post_missing_role(self):
        resp = self.client.post(
            self.detail_url,
            data=json.dumps({"toys": "fun"}),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        result = json.loads(resp.content)
        self.assertIn("error", result)
        self.assert_not_enrolled()

    def test_detail_post_no_json(self):
        resp = self.client.post(
            self.detail_url,
            data={"role": "staff"},
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 204)
        # reload user from DB
        ext_user = User.objects.get(email=self.ext_user.email)
        groups = [g.name for g in ext_user.groups.all()]
        self.assertIn(self.staff_groupname, groups)
        self.assertNotIn(self.inst_groupname, groups)
        self.assert_enrolled()

    def test_detail_delete_staff(self):
        group, _ = Group.objects.get_or_create(name=self.staff_groupname)
        self.ext_user.groups.add(group)
        self.ext_user.save()

        resp = self.client.delete(
            self.detail_url,
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 204)
        # reload user from DB
        ext_user = User.objects.get(email=self.ext_user.email)
        groups = [g.name for g in ext_user.groups.all()]
        self.assertNotIn(self.staff_groupname, groups)

    def test_detail_delete_instructor(self):
        group, _ = Group.objects.get_or_create(name=self.inst_groupname)
        self.user.groups.add(group)
        self.ext_user.groups.add(group)
        self.user.save()
        self.ext_user.save()

        resp = self.client.delete(
            self.detail_url,
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 204)
        # reload user from DB
        ext_user = User.objects.get(email=self.ext_user.email)
        groups = [g.name for g in ext_user.groups.all()]
        self.assertNotIn(self.inst_groupname, groups)

    def test_delete_last_instructor(self):
        group, _ = Group.objects.get_or_create(name=self.inst_groupname)
        self.ext_user.groups.add(group)
        self.ext_user.save()

        resp = self.client.delete(
            self.detail_url,
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        result = json.loads(resp.content)
        self.assertIn("error", result)
        # reload user from DB
        ext_user = User.objects.get(email=self.ext_user.email)
        groups = [g.name for g in ext_user.groups.all()]
        self.assertIn(self.inst_groupname, groups)

    def test_post_last_instructor(self):
        group, _ = Group.objects.get_or_create(name=self.inst_groupname)
        self.ext_user.groups.add(group)
        self.ext_user.save()

        resp = self.client.post(
            self.detail_url,
            data={"role": "staff"},
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        result = json.loads(resp.content)
        self.assertIn("error", result)
        # reload user from DB
        ext_user = User.objects.get(email=self.ext_user.email)
        groups = [g.name for g in ext_user.groups.all()]
        self.assertIn(self.inst_groupname, groups)

    def test_permission_denied_self(self):
        group, _ = Group.objects.get_or_create(name=self.staff_groupname)
        self.user.groups.add(group)
        self.user.is_staff = False
        self.user.save()

        self_url = self.location.url_reverse('course_team', self.user.email)

        resp = self.client.post(
            self_url,
            data={"role": "instructor"},
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        result = json.loads(resp.content)
        self.assertIn("error", result)

    def test_permission_denied_other(self):
        group, _ = Group.objects.get_or_create(name=self.staff_groupname)
        self.user.groups.add(group)
        self.user.is_staff = False
        self.user.save()

        resp = self.client.post(
            self.detail_url,
            data={"role": "instructor"},
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        result = json.loads(resp.content)
        self.assertIn("error", result)

    def test_staff_can_delete_self(self):
        group, _ = Group.objects.get_or_create(name=self.staff_groupname)
        self.user.groups.add(group)
        self.user.is_staff = False
        self.user.save()

        self_url = self.location.url_reverse('course_team', self.user.email)

        resp = self.client.delete(self_url)
        self.assertEqual(resp.status_code, 204)
        # reload user from DB
        user = User.objects.get(email=self.user.email)
        groups = [g.name for g in user.groups.all()]
        self.assertNotIn(self.staff_groupname, groups)

    def test_staff_cannot_delete_other(self):
        group, _ = Group.objects.get_or_create(name=self.staff_groupname)
        self.user.groups.add(group)
        self.user.is_staff = False
        self.user.save()
        self.ext_user.groups.add(group)
        self.ext_user.save()

        resp = self.client.delete(self.detail_url)
        self.assertEqual(resp.status_code, 400)
        result = json.loads(resp.content)
        self.assertIn("error", result)
        # reload user from DB
        ext_user = User.objects.get(email=self.ext_user.email)
        groups = [g.name for g in ext_user.groups.all()]
        self.assertIn(self.staff_groupname, groups)

    def test_user_not_initially_enrolled(self):
        # Verify that ext_user is not enrolled in the new course before being added as a staff member.
        self.assert_not_enrolled()

    def test_remove_staff_does_not_unenroll(self):
        # Add user with staff permissions.
        self.client.post(
            self.detail_url,
            data=json.dumps({"role": "staff"}),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
        )
        self.assert_enrolled()
        # Remove user from staff on course. Will not un-enroll them from the course.
        resp = self.client.delete(
            self.detail_url,
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 204)
        self.assert_enrolled()

    def test_staff_to_instructor_still_enrolled(self):
        # Add user with staff permission.
        self.client.post(
            self.detail_url,
            data=json.dumps({"role": "staff"}),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
        )
        self.assert_enrolled()
        # Now add with instructor permission. Verify still enrolled.
        resp = self.client.post(
            self.detail_url,
            data=json.dumps({"role": "instructor"}),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(resp.status_code, 204)
        self.assert_enrolled()

    def assert_not_enrolled(self):
        """ Asserts that self.ext_user is not enrolled in self.course. """
        self.assertFalse(
            CourseEnrollment.is_enrolled(self.ext_user, self.course.location.course_id),
            'Did not expect ext_user to be enrolled in course'
        )

    def assert_enrolled(self):
        """ Asserts that self.ext_user is enrolled in self.course. """
        self.assertTrue(
            CourseEnrollment.is_enrolled(self.ext_user, self.course.location.course_id),
            'User ext_user should have been enrolled in the course'
        )
