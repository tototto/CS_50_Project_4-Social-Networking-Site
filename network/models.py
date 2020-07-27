from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Post(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE, related_name="PostOwner")
    PostContent = models.CharField(max_length=100)
    DateTime = models.DateTimeField()
    Likes = models.IntegerField(default=0)

    def __str__(self):
        return f"User: {self.User}, Post: {self.PostContent}, On {self.DateTime}, has {self.Likes} Likes"
    
class Follower(models.Model):
    UserAcct = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UserAcctFollower")
    Followers = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UsersFollower")

    def __str__(self):
        return f"{self.UserAcct} has {self.Followers} as a Follower"

class Following(models.Model):
    UserAcct = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UserAcctFollowing")
    Followings = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UsersFollowing")

    def __str__(self):
        return f"{self.UserAcct} is following {self.Followings}"

# class AccountStatus(models.Model):
#    User = models.ForeignKey(User, on_delete=models.CASCADE, related_name="AcctOwner")
#    Following = models.ForeignKey(Following, on_delete=models.CASCADE, related_name="following")
#    Follower = models.ForeignKey(Follower, on_delete=models.CASCADE, related_name="follower")