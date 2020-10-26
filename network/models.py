from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    #https://stackoverflow.com/a/41848546 found a solution by using symmetrical=False
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)


class Post(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField('User', related_name="liked_posts", blank=True) #could create a class for likes, but (for now) we only need the user

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %-d %Y, %-I:%M %p"),
            "likes": self.likes
        }
