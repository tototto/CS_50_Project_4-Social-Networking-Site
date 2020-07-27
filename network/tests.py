from django.test import TestCase, Client
import unittest

from .views import *
from .models import * 
from datetime import datetime

# Create your tests here.

# This is a Test Suite
class NetworkAppTest(TestCase):

    # This is an initial Setup. To ensure there are some data the Testcase can Work with and Test with:
    # when you run the Unit test Django will create another seperate database for you just for Testing
    # Test DB is destroyed when the Unit Test finish running
    def setUp(self):
        # Add sample Test data into Test databse (will not affect actual DB)

        # Create Users.
        user1 = User.objects.create(username='user1', password='12345', email='abc@example.com')
        user2 = User.objects.create(username='user2', password='12345', email='cde@example.com')
        user3 = User.objects.create(username='user3', password='12345', email='pol@example.com')
        # Create Posts.
        User1Post = Post.objects.create(User=user1, PostContent='abc', DateTime=datetime.now(), Likes=0)
        User2Post = Post.objects.create(User=user2, PostContent='def', DateTime=datetime.now(), Likes=0)
        # Create Following & Follower
        User1HasUser2AsFollower = Follower.objects.create(UserAcct=user1, Followers=user2)
        User2isFollowingUser1 = Following.objects.create(UserAcct=user2, Followings=user1)
    
    # This is a TestCase in the Test Suite
    def test_NoPostMade(self):
        FreshUser = User.objects.get(username='user3')
        PostNotExists = Post.objects.filter(User=FreshUser)
        self.assertFalse(PostNotExists)

    # This is another TestCase in the Test Suite
    def test_Following(self):
        User1 = User.objects.get(username='user1')
        User2 = User.objects.get(username='user2')

        User2Followuser1 = Following.objects.get(UserAcct=User2, Followings=User1)
        self.assertTrue(User2Followuser1)

    def test_Follower(self):
        User1 = User.objects.get(username='user1')
        User2 = User.objects.get(username='user2')
        
        User1HasUser2AsFollower = Follower.objects.get(UserAcct=User1, Followers=User2)
        self.assertTrue(User1HasUser2AsFollower)

    def test_View_Function_for_AlreadyFollowing(self):
        """
        Test for User's that has a Follower
        """
        User1 = User.objects.get(username='user1')
        User2 = User.objects.get(username='user2')

        self.assertTrue(CheckIfAlreadyFollowing(User2, User1))

    def test_View_Function_for_Not_AlreadyFollowing(self):
        """
        Test for User's that has no Follower
        """
        User3 = User.objects.get(username='user3')
        User2 = User.objects.get(username='user2')

        self.assertFalse(CheckIfAlreadyFollowing(User2, User3))

    def test_index(self):
        c = Client()
        response = c.get("")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context["page_obj"]), "<Page 1 of 1>")

    def test_valid_Profile_Page(self):
        User = 'NonExistantUser'
        c = Client()
        response = c.get(f"profile/{User}")
        self.assertEqual(response.status_code, 404)


    



        