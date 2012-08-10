"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime

from django.test import TestCase

from .models import User, UserProfile, CourseEnrollment, replicate_user, USER_FIELDS_TO_COPY

COURSE_1 = 'edX/toy/2012_Fall'
COURSE_2 = 'edx/full/6.002_Spring_2012'

class ReplicationTest(TestCase):

    multi_db = True

    def test_user_replication(self):
        """Test basic user replication."""
        portal_user = User.objects.create_user('rusty', 'rusty@edx.org', 'fakepass')
        portal_user.first_name='Rusty'
        portal_user.last_name='Skids'
        portal_user.is_staff=True
        portal_user.is_active=True
        portal_user.is_superuser=True
        portal_user.last_login=datetime(2012, 1, 1)
        portal_user.date_joined=datetime(2011, 1, 1)
        # This is an Askbot field and will break if askbot is not included
        portal_user.seen_response_count = 10

        portal_user.save(using='default')

        # We replicate this user to Course 1, then pull the same user and verify
        # that the fields copied over properly.
        replicate_user(portal_user, COURSE_1)
        course_user = User.objects.using(COURSE_1).get(id=portal_user.id)

        # Make sure the fields we care about got copied over for this user.
        for field in USER_FIELDS_TO_COPY:
            self.assertEqual(getattr(portal_user, field),
                             getattr(course_user, field),
                             "{0} not copied from {1} to {2}".format(
                                 field, portal_user, course_user
                             ))

        # Since it's the first copy over of User data, we should have all of it
        self.assertEqual(portal_user.seen_response_count,
                         course_user.seen_response_count)

        # But if we replicate again, the user already exists in the Course DB,
        # so it shouldn't update the seen_response_count (which is Askbot 
        # controlled)
        portal_user.seen_response_count = 20
        replicate_user(portal_user, COURSE_1)
        course_user = User.objects.using(COURSE_1).get(id=portal_user.id)
        self.assertEqual(portal_user.seen_response_count, 20)
        self.assertEqual(course_user.seen_response_count, 10)

        # Another replication should work for an email change however, since
        # it's a field we care about.
        portal_user.email = "clyde@edx.org"
        replicate_user(portal_user, COURSE_1)
        course_user = User.objects.using(COURSE_1).get(id=portal_user.id)
        self.assertEqual(portal_user.email, course_user.email)

        # During this entire time, the user data should never have made it over
        # to COURSE_2
        self.assertRaises(User.DoesNotExist, 
                          User.objects.using(COURSE_2).get,
                          id=portal_user.id)


    def test_enrollment_for_existing_user_info(self):
        """Test the effect of Enrolling in a class if you've already got user
        data to be copied over."""
        # Create our User
        portal_user = User.objects.create_user('jack', 'jack@edx.org', 'fakepass')
        portal_user.first_name = "Jack"
        portal_user.save()

        # Set up our UserProfile info
        portal_user_profile = UserProfile.objects.create(
                                  user=portal_user,
                                  name="Jack Foo",
                                  level_of_education=None,
                                  gender='m',
                                  mailing_address=None,
                                  goals="World domination",
                              )
        portal_user_profile.save()

        # Now let's see if creating a CourseEnrollment copies all the relevant
        # data.
        portal_enrollment = CourseEnrollment.objects.create(user=portal_user,
                                                            course_id=COURSE_1)
        portal_enrollment.save()

        # Grab all the copies we expect
        course_user = User.objects.using(COURSE_1).get(id=portal_user.id)
        self.assertEquals(portal_user, course_user)
        self.assertRaises(User.DoesNotExist, 
                          User.objects.using(COURSE_2).get,
                          id=portal_user.id)

        course_enrollment = CourseEnrollment.objects.using(COURSE_1).get(id=portal_enrollment.id)
        self.assertEquals(portal_enrollment, course_enrollment)
        self.assertRaises(CourseEnrollment.DoesNotExist, 
                          CourseEnrollment.objects.using(COURSE_2).get,
                          id=portal_enrollment.id)

        course_user_profile = UserProfile.objects.using(COURSE_1).get(id=portal_user_profile.id)
        self.assertEquals(portal_user_profile, course_user_profile)
        self.assertRaises(UserProfile.DoesNotExist, 
                          UserProfile.objects.using(COURSE_2).get,
                          id=portal_user_profile.id)


    def test_enrollment_for_user_info_after_enrollment(self):
        """Test the effect of Enrolling in a class if you've already got user
        data to be copied over."""
        # Create our User
        portal_user = User.objects.create_user('jack', 'jack@edx.org', 'fakepass')
        portal_user.first_name = "Jack"
        portal_user.save()

        # Now let's see if creating a CourseEnrollment copies all the relevant
        # data when things are saved.
        portal_enrollment = CourseEnrollment.objects.create(user=portal_user,
                                                            course_id=COURSE_1)
        portal_enrollment.save()

        # Set up our UserProfile info
        portal_user_profile = UserProfile.objects.create(
                                  user=portal_user,
                                  name="Jack Foo",
                                  level_of_education=None,
                                  gender='m',
                                  mailing_address=None,
                                  goals="World domination",
                              )
        portal_user_profile.save()
        
        # Grab all the copies we expect, and make sure it doesn't end up in 
        # places we don't expect.
        course_user = User.objects.using(COURSE_1).get(id=portal_user.id)
        self.assertEquals(portal_user, course_user)
        self.assertRaises(User.DoesNotExist, 
                          User.objects.using(COURSE_2).get,
                          id=portal_user.id)

        course_enrollment = CourseEnrollment.objects.using(COURSE_1).get(id=portal_enrollment.id)
        self.assertEquals(portal_enrollment, course_enrollment)
        self.assertRaises(CourseEnrollment.DoesNotExist, 
                          CourseEnrollment.objects.using(COURSE_2).get,
                          id=portal_enrollment.id)

        course_user_profile = UserProfile.objects.using(COURSE_1).get(id=portal_user_profile.id)
        self.assertEquals(portal_user_profile, course_user_profile)
        self.assertRaises(UserProfile.DoesNotExist, 
                          UserProfile.objects.using(COURSE_2).get,
                          id=portal_user_profile.id)







