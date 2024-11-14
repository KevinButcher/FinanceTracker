from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver # simplify connecting functions to signals
from django.db.models.signals import post_save # execute a function after something is executed
from django.conf import settings

# Create your models here.

# make it so the email fields can't be blank and that the email is unique
User._meta.get_field('email').blank = False
User._meta.get_field('email').null = False
User._meta.get_field('email')._unique = True

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profilepic.jpg', upload_to='profile_pictures')
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
    
# signal to automatically create a profile instance after a user is created, receiver specifies when to ran after receiving signal
@receiver(post_save, sender=settings.AUTH_USER_MODEL) # settings.AUTH_USER_MODEL allows for referencing the user model configured in settings.py
def auto_create_profile(sender, instance, created, **kwargs): # kwargs stands for keyword arguments (instance, created, etc.)
    if created:
        Profile.objects.get_or_create(user=instance)
