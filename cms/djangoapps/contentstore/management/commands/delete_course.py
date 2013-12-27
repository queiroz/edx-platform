###
### Script for cloning a course
###
from django.core.management.base import BaseCommand, CommandError
from .prompt import query_yes_no
from contentstore.utils import delete_course_and_groups
from student.models import get_user_by_username_or_email
from student.roles import GlobalStaff
from django.core.exceptions import PermissionDenied


#
# To run from command line: rake cms:delete_course LOC=edX/111/Foo1
#
class Command(BaseCommand):
    help = '''Delete a MongoDB backed course'''

    def handle(self, *args, **options):
        if 3 >= len(args) >= 2:
            raise CommandError("delete_course requires 2 or 3 arguments: <staff_user_id> <location> |commit|")

        staff_user = get_user_by_username_or_email(args[0])
        # note: does not require them to authenticate themselves.
        if not GlobalStaff().has_user(staff_user):
            raise PermissionDenied
        course_id = args[1]

        commit = False
        if len(args) == 3:
            commit = args[2] == 'commit'

        if commit:
            print('Actually going to delete the course from DB....')

        if query_yes_no("Deleting course {0}. Confirm?".format(course_id), default="no"):
            if query_yes_no("Are you sure. This action cannot be undone!", default="no"):
                delete_course_and_groups(staff_user, course_id, commit)
