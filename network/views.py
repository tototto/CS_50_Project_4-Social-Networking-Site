from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.db.models import Count
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

from .models import *


def index(request):
    AllPosts = Post.objects.all().order_by('DateTime').reverse()
    paginator = Paginator(AllPosts, 10) # Show 10 posts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render posts as Paginated set of pages
    return render(request, "network/index.html", {
        'page_obj': page_obj
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()

        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def createPost(request):
    if request.method == "POST":
        NewPostContent = request.POST["NewPost"]
        username = request.user.username
        CurrUser = GetCurrUserObject(username)
        DateTimeOfPost = datetime.now()
        Like = 0

        PostCreated = Post.objects.create(User=CurrUser, PostContent=NewPostContent, DateTime=DateTimeOfPost, Likes=Like)
        PostCreated.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "network/createPost.html")

def GetCurrUserObject(Username):
    return User.objects.get(username=Username)

def profileUser(request, username):
    CurrUser = request.user.username

    AllPosts = Post.objects.filter(User=GetCurrUserObject(username)).order_by('DateTime').reverse()

    NumberOfFollower = len(Follower.objects.filter(UserAcct=GetCurrUserObject(username)))
    NumberFollowing = len(Following.objects.filter(UserAcct=GetCurrUserObject(username)))

    # Check if Already Following User
    FollowingOrNot = True if CheckIfAlreadyFollowing(request.user.username, username) else False

    return render(request, "network/profile.html", {
         "UserFollowers": NumberOfFollower,
         "UserFollowings": NumberFollowing,
         "AllPosts": AllPosts,
         "ProfileUser": username,
         "FollowingStatus": FollowingOrNot
    })

# This is an API to FOLLOW / UNFOLLOW users
@login_required
def followUser(request):

    # Composing a new follow / unfollow request must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get json Data
    data = json.loads(request.body)

    # Grab json Content
    FollowingUser = data.get("following", "")
    CurrUser = request.user.username

    # Check if Curr User is already following the Selected User
    if len(CheckIfAlreadyFollowing(CurrUser,FollowingUser)) == 0 :
        # If not add him to Following List
        addFollowing = Following.objects.create(UserAcct=GetCurrUserObject(CurrUser), Followings=GetCurrUserObject(FollowingUser))
        addFollowing.save()
        # Set up the Follower Relationship As well
        addFollower = Follower.objects.create(UserAcct=GetCurrUserObject(FollowingUser), Followers=GetCurrUserObject(CurrUser))
        addFollower.save()

        return JsonResponse({"message": "Sucessfully Followed user " + FollowingUser + "."}, status=201)
    else:
        # Delete from Following 
        FollowingToBeDeleted = Following.objects.filter(UserAcct=GetCurrUserObject(CurrUser), Followings=GetCurrUserObject(FollowingUser))
        FollowingToBeDeleted.delete()
        # Delete from Follower
        FollowerToBeDeleted = Follower.objects.filter(UserAcct=GetCurrUserObject(FollowingUser), Followers=GetCurrUserObject(CurrUser))
        FollowerToBeDeleted.delete()

        return JsonResponse({"message": "Sucessfully Unfollowed user " + FollowingUser + "."}, status=201)

    return JsonResponse({"error": "Failed to Follow or Unfollow User " + FollowingUser + "."}, status=400)

# This is an API to Save Edit post
def editPost(request):
    # Saving an existing Twitter Posting must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    # Get json Data
    data = json.loads(request.body)

    # Grab json Content
    PostID = data.get("PostID", "")
    NewPostContent = data.get("NewPostContent", "")

    # Update User's New Post Content into DB
    PostToBeUpdated = Post.objects.get(id=PostID)
    if PostToBeUpdated is not None:
        PostToBeUpdated.PostContent = NewPostContent
        PostToBeUpdated.save(update_fields=['PostContent'])
        return JsonResponse({"message": "Sucessfully Updated Post."}, status=201)

    return JsonResponse({"error": "No such Post Exists"}, status=400)

# This is an API to update post's Like
def ThumbsUp(request):
    if request.method != "POST":
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Get json Data
    data = json.loads(request.body)

    # Grab json Content
    PostID = data.get("PostID")

    # Increment this Post Data Object Like by 1 
    PostToBeUpdated = Post.objects.get(id=PostID)
    if PostToBeUpdated is not None:
        PostToBeUpdated.Likes += 1
        PostToBeUpdated.save(update_fields=['Likes'])
        return JsonResponse({"message": "incremented LIKE for current Post with ID " + PostID + "."}, status=201)

    return JsonResponse({"error": "No such Post Exists"}, status=400)

# This is an API to update post's Unlike
def ThumbsDown(request):
    if request.method != "POST":
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Get json Data
    data = json.loads(request.body)

    # Grab json Content
    PostID = data.get("PostID")

    # Increment this Post Data Object Like by 1 
    PostToBeUpdated = Post.objects.get(id=PostID)
    if PostToBeUpdated is not None:
        PostToBeUpdated.Likes -= 1
        PostToBeUpdated.save(update_fields=['Likes'])
        return JsonResponse({"message": "decremented LIKE for current Post with ID " + PostID + "."}, status=201)

    return JsonResponse({"error": "No such Post Exists"}, status=400)

@login_required
def following(request):
    # Show all Post of User CurrUser is following, Grouped By Users
    FollowingUserList = []
    AllFollowingUsers = Following.objects.all()
    for EachFollowing in AllFollowingUsers:
        FollowingUserList.append(EachFollowing.Followings)

    AllPosts = []
    for EachUser in FollowingUserList:
        AllPosts.append(Post.objects.filter(User=EachUser).order_by('DateTime').reverse())

    return render(request, "network/followingPosts.html", {
        "AllFollowingUsersPost": AllPosts,
    })


def CheckIfAlreadyFollowing(User, followingName):
    return Following.objects.filter(UserAcct=GetCurrUserObject(User),Followings=GetCurrUserObject(followingName))

