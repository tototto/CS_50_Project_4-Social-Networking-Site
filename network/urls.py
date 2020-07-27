
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.createPost, name="createPost"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("followUser", views.followUser, name="followUser"),
    path("following", views.following, name="following"),
    path("editPost", views.editPost, name="editPost"),
    path("ThumbsUp", views.ThumbsUp, name="ThumbsUp"),
    path("ThumbsDown", views.ThumbsDown, name="ThumbsDown"),
    path("profile/<str:username>", views.profileUser, name="profileUser")
]
