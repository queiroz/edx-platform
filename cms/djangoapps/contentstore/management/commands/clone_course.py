"""
Script for cloning a course
"""
from django.core.management.base import BaseCommand, CommandError
from xmodule.modulestore.store_utilities import clone_course
from xmodule.modulestore.django import modulestore
from xmodule.contentstore.django import contentstore
from xmodule.course_module import CourseDescriptor
from student.roles import CourseInstructorRole, CourseStaffRole, GlobalStaff, CourseCreatorRole
from student.models import get_user_by_username_or_email
from django.core.exceptions import PermissionDenied


#
# To run from command line: rake cms:clone SOURCE_LOC=edX/111/Foo1 DEST_LOC=edX/135/Foo3
#
class Command(BaseCommand):
    """Clone a MongoDB-backed course to another location"""
    help = 'Clone a MongoDB backed course to another location'

    def handle(self, *args, **options):
        "Execute the command"
        if len(args) != 3:
            raise CommandError("clone requires 3 arguments: <staff_user_id> <source-course_id> <dest-course_id>")

        staff_user = get_user_by_username_or_email(args[0])
        # note: does not require them to authenticate themselves.
        if not (GlobalStaff().has_user(staff_user) or CourseCreatorRole().has_user(staff_user)):
            raise PermissionDenied
        source_course_id = args[1]
        dest_course_id = args[2]

        mstore = modulestore('direct')
        cstore = contentstore()

        org, course_num, _ = dest_course_id.split("/")
        mstore.ignore_write_events_on_courses.append('{0}/{1}'.format(org, course_num))

        print("Cloning course {0} to {1}".format(source_course_id, dest_course_id))

        source_location = CourseDescriptor.id_to_location(source_course_id)
        dest_location = CourseDescriptor.id_to_location(dest_course_id)

        if clone_course(mstore, cstore, source_location, dest_location):
            # be sure to recompute metadata inheritance after all those updates
            mstore.refresh_cached_metadata_inheritance_tree(dest_location)

            print("copying User permissions...")
            CourseInstructorRole(dest_location).add_users(
                staff_user,
                *CourseInstructorRole(source_location).users_with_role()
            )
            CourseStaffRole(dest_location).add_users(
                staff_user,
                *CourseStaffRole(source_location).users_with_role()
            )
