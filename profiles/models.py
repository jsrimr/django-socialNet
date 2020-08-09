from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify

from .utils import get_random_code


# Create your models here.

class ProfileManager(models.Manager):
    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles

    def get_all_profiles_to_invite(self, sender):
        all_profiles_except_sender = Profile.objects.all().exclude(user=sender)
        profile_sender = Profile.objects.get(user=sender)
        qs = Relationship.objects.filter(Q(sender=profile_sender) | Q(receiver=profile_sender))
        accepted = set()
        for rel in qs:
            if rel.status == 'accepted':
                accepted.add(rel.receiver)
                accepted.add(rel.sender)

        available = [profile for profile in all_profiles_except_sender if profile not in accepted]
        return available


class Profile(models.Model):
    objects = ProfileManager()
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="no bio...")
    email = models.EmailField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(default='avatar.jpeg', upload_to='avatars/')

    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    slug = models.SlugField(unique=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}-{self.created.strftime('%d-%m-%Y')}"

    def save(self, *args, **kwargs):
        ex = False
        if self.first_name and self.last_name:
            to_slug = slugify(str(self.first_name) + " " + str(self.last_name))
            ex = Profile.objects.filter(slug=to_slug).exists()

            while ex:
                to_slug = slugify(to_slug + " " + str(get_random_code()))
                ex = Profile.objects.filter(slug=to_slug).exists()

        else:
            to_slug = str(self.user)

        self.slug = to_slug

        super().save(*args, **kwargs)

    def get_friends(self):
        return self.friends.all()

    def get_friends_count(self):
        return self.friends.all().count()

    def get_post_no(self):
        return self.posts.all().count()

    def fet_all_authors_posts(self):
        return self.posts.all()

    def get_likes_given_no(self):
        likes = self.like_set.all()
        total_liked = 0
        for item in likes:
            if item.value == 'Like':
                total_liked += 1
        return total_liked

    def get_likes_received(self):
        posts = self.posts.all()
        total_liked = 0
        for item in posts:
            total_liked += item.liked.all().count()
        return total_liked


STATUS_CHOICES = (
    ('send', 'send'),
    ('accepted', 'accepted')
)


class RelationshipManager(models.Manager):
    def invitations_received(self, receiver):
        qs = Relationship.objects.filter(receiver=receiver, status='send')
        return qs



class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = RelationshipManager()

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
