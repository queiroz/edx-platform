from ..utils import get_course_location_for_item
from xmodule.modulestore.locator import CourseLocator
from student.roles import CourseRole, CourseStaffRole, CourseInstructorRole


def has_access(user, location, role=CourseStaffRole.ROLE):
    """
    Return True if user allowed to access this piece of data
    Note that the CMS permissions model is with respect to courses
    There is a super-admin permissions if user.is_staff is set
    Also, since we're unifying the user database between LMS and CAS,
    I'm presuming that the course instructor (formally known as admin)
    will not be in both INSTRUCTOR and STAFF groups, so we have to cascade our
    queries here as INSTRUCTOR has all the rights that STAFF do
    """
    if user.is_staff:
        return True
    if not isinstance(location, CourseLocator):
        location = get_course_location_for_item(location)
    _has_access = CourseRole(role, location).has_user(user)
    # if we're not in STAFF, perhaps we're in INSTRUCTOR groups
    if not _has_access and role == CourseStaffRole.ROLE:
        _has_access = CourseInstructorRole(location).has_user(user)
    return _has_access
