import json
from functools import partial
import factory
from factory.django import DjangoModelFactory

# Imported to re-export
# pylint: disable=unused-import
from student.tests.factories import UserFactory  # Imported to re-export
from student.tests.factories import GroupFactory  # Imported to re-export
from student.tests.factories import CourseEnrollmentAllowedFactory  # Imported to re-export
from student.tests.factories import RegistrationFactory  # Imported to re-export
# pylint: enable=unused-import

from student.tests.factories import UserProfileFactory as StudentUserProfileFactory, AdminFactory
from courseware.models import StudentModule, XModuleUserStateSummaryField
from courseware.models import XModuleStudentInfoField, XModuleStudentPrefsField
from student.roles import (
    CourseInstructorRole,
    CourseStaffRole,
    CourseBetaTesterRole,
    GlobalStaff,
    OrgStaffRole,
    OrgInstructorRole,
)

from xmodule.modulestore import Location


location = partial(Location, 'i4x', 'edX', 'test_course', 'problem')


class UserProfileFactory(StudentUserProfileFactory):
    courseware = 'course.xml'


class InstructorFactory(UserFactory):
    """
    Given a course Location, returns a User object with instructor
    permissions for `course`.
    """
    last_name = "Instructor"

    @factory.post_generation
    def course(self, create, extracted, admin=None, **kwargs):
        if extracted is None:
            raise ValueError("Must specify a course location for a course instructor user")
        CourseInstructorRole(extracted).add_users(admin or AdminFactory(), self)


class StaffFactory(UserFactory):
    """
    Given a course Location, returns a User object with staff
    permissions for `course`.
    """
    last_name = "Staff"

    @factory.post_generation
    def course(self, create, extracted, admin=None, **kwargs):
        if extracted is None:
            raise ValueError("Must specify a course location for a course staff user")
        CourseStaffRole(extracted).add_users(admin or AdminFactory(), self)


class BetaTesterFactory(UserFactory):
    """
    Given a course Location, returns a User object with beta-tester
    permissions for `course`.
    """
    last_name = "Beta-Tester"

    @factory.post_generation
    def course(self, create, extracted, admin=None, **kwargs):
        if extracted is None:
            raise ValueError("Must specify a course location for a beta-tester user")
        CourseBetaTesterRole(extracted).add_users(admin, self)


class OrgStaffFactory(UserFactory):
    """
    Given a course Location, returns a User object with org-staff
    permissions for `course`.
    """
    last_name = "Org-Staff"

    @factory.post_generation
    def course(self, create, extracted, admin=None, **kwargs):
        if extracted is None:
            raise ValueError("Must specify a course location for an org-staff user")
        OrgStaffRole(extracted).add_users(admin, self)


class OrgInstructorFactory(UserFactory):
    """
    Given a course Location, returns a User object with org-instructor
    permissions for `course`.
    """
    last_name = "Org-Instructor"

    @factory.post_generation
    def course(self, create, extracted, admin=None, **kwargs):
        if extracted is None:
            raise ValueError("Must specify a course location for an org-instructor user")
        OrgInstructorRole(extracted).add_users(admin, self)


class GlobalStaffFactory(UserFactory):
    """
    Returns a User object with global staff access
    """
    last_name = "GlobalStaff"

    @factory.post_generation
    def set_staff(self, create, extracted, admin=None, **kwargs):
        GlobalStaff().add_users(admin, self)


class StudentModuleFactory(DjangoModelFactory):
    FACTORY_FOR = StudentModule

    module_type = "problem"
    student = factory.SubFactory(UserFactory)
    course_id = "MITx/999/Robot_Super_Course"
    state = None
    grade = None
    max_grade = None
    done = 'na'


class UserStateSummaryFactory(DjangoModelFactory):
    FACTORY_FOR = XModuleUserStateSummaryField

    field_name = 'existing_field'
    value = json.dumps('old_value')
    usage_id = location('def_id').url()


class StudentPrefsFactory(DjangoModelFactory):
    FACTORY_FOR = XModuleStudentPrefsField

    field_name = 'existing_field'
    value = json.dumps('old_value')
    student = factory.SubFactory(UserFactory)
    module_type = 'MockProblemModule'


class StudentInfoFactory(DjangoModelFactory):
    FACTORY_FOR = XModuleStudentInfoField

    field_name = 'existing_field'
    value = json.dumps('old_value')
    student = factory.SubFactory(UserFactory)
