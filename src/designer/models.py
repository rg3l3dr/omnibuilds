from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from guardian.shortcuts import assign_perm
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from invitations.signals import invite_accepted
from invitations.views import AcceptInvite
from invitations.models import Invitation
from notifications.signals import notify
from django.utils import timezone

""" Django.contrib.auth Models

	class User(models.Model):
		first_name = models.CharField(null=True, blank=True, max_length=30)
		last_name = models.CharField(null=True, blank=True, max_length=30)
		email = models.Emailfield(null=True, blank=True)
		password = models.HashField()
		groups = models.ManytoManyField(Group)
		user_permissions = models.ManytoManyField(Permission)
		is_staff = models.BooleanField()
		is_active = models.BooleanField()
		is_superuser = models.BooleanField()
		last_login = models.DateTimeField()
		date_joined = models.DateTimeField()

	class Permission(models.Model):
		name = models.CharField(max_length=255)
		content_type = models.ForeignKey(ContentType)
		codename = models.CharField(max_length=100)

	class Group(models.Model):
		name = models.CharField(max_length=80)
		permisssions = models.ManytoManyField(Permission)
"""

def profile_media_upload_location(instance, filename):
	location = str(instance.name)
	return "%s/%s" %(location, filename)

def repo_media_upload_location(instance, filename):
	location = str(instance.owner.profile_name)
	return "%s/%s" %(location, filename)

class Signup(models.Model):
	first_name = models.CharField(max_length=30, null=True, blank=True)
	last_name = models.CharField(max_length=30, null=True, blank=True)
	email = models.EmailField()
	beta = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

class SubPlan(models.Model):
	name = models.CharField(max_length=30)
	description = models.TextField(null=True, blank=True)
	rate = models.IntegerField()

	def __unicode__(self):
		return unicode(self.name)

class License(models.Model):
	short_name = models.CharField(max_length=30)
	long_name = models.CharField(max_length=100)
	description = models.TextField()
	link = models.URLField()

	def __unicode__(self):
		return unicode(self.short_name)

class Profile(models.Model):
	user = models.OneToOneField(User)
	name = models.CharField(max_length=30, unique=True)
	slug = models.SlugField(max_length=30, unique=True)
	about = models.TextField(null=True, blank=True)
	location = models.CharField(max_length=120, null=True, blank=True)
	picture = models.ImageField(upload_to=profile_media_upload_location, null=True, blank=True)
	website = models.URLField(max_length=50, null=True, blank=True)
	subplan = models.ForeignKey(SubPlan, default=1)
	data = models.BigIntegerField(default=0)
	data_cap = models.BigIntegerField(default=100000000)
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return unicode(self.name)

	def get_absolute_url(self):
		url = reverse("profile")
		return url

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Profile, self).save(*args, **kwargs)

	class Meta:
		permissions = (
			("view_profile", "Can see all profile info"),
			("edit_profile", "Can edit any profile info"),
			("profile_admin", "Can change settings for a profile"),
		)

""" Profile Workflow

	1. Visitor signs up and creates a user account
	2. A UserProfile should be created for that user automatically (only once) as a post save method on the User Model
	3. If user creates a team a TeamProfile should be created (for each team)
	4. When the user signs in, how do you know if they are signed in as user or team profile?
	5. A user should never be acting as a team, only on behalf of a team, if they are a member or owner, but will need a way to track what team the user is currently logged into
"""
# trigger events when invite is accpeted, removed since this is triggered as soon as the email link is clicked, does not confirm that the recipient actually joins the site
# @receiver(invite_accepted, sender=AcceptInvite)
# def increase_data_cap(sender, email, **kwargs):
# 	invite = get_object_or_404(Invitation, email=email)
# 	user_profile = get_object_or_404(UserProfile, user=invite.inviter)
# 	user_profile.data_cap += 100
# 	user_profile.save()
# 	new_user = get_object_or_404(User, email=email)

@receiver(post_save, sender=User)
def create_user_profile(sender, created, instance, **kwargs):

    if created:
    	user_profile, created = UserProfile.objects.get_or_create(user=instance)

    	if created: 
	    	user_profile.name = instance.username
	        user_profile.save()
	        profile = get_object_or_404(Profile, user=user_profile.user)
	        assign_perm('edit_profile', user_profile.user, profile)
	        assign_perm('profile_admin', user_profile.user, profile)

	        # check to see if this user was invited	        	
        	invites = Invitation.objects.filter(email = user_profile.user.email)
        	if invites.count() >= 1: 
	        	# in case multiple users have invited new user, take the first invite
	        	invite = invites[0]

	        	# increase data plan for the inviter
	        	inviter_profile = get_object_or_404(UserProfile, user=invite.inviter)
	        	inviter_profile.data_cap += 100000000
	        	inviter_profile.save()

	        	# notify the inviter, the invitation has been accepted
	        	notify.send(user_profile, recipient=inviter_profile.user, verb='accepted your invitation')


class UserProfile(Profile):
	public_name = models.CharField(max_length=50, null=True, blank=True)
	public_email = models.EmailField(null=True, blank=True)



class TeamProfile(Profile):
	members = models.ManyToManyField(User, related_name='team_members')
	public = models.BooleanField(default=True)
	created_at = models.DateTimeField()
	last_updated = models.DateTimeField()

class Customer(models.Model):
	user_profile = models.ForeignKey(UserProfile, null=True, blank=True)
	team_profile = models.ForeignKey(TeamProfile, null=True, blank=True)
	sub_plan = models.ForeignKey(SubPlan)
	stripe_customer_id = models.CharField(max_length=40)
	card_brand = models.CharField(max_length=20)
	card_last4 = models.CharField(max_length=5)
	card_exp_month = models.CharField(max_length=5)
	card_exp_year = models.CharField(max_length=5)
	next_payment = models.DateTimeField()
	active = models.BooleanField(default=True)
	failed_count = models.IntegerField(default=0)

	def __unicode__(self):
		if self.user_profile:
			return unicode(self.user_profile)
		else:
			return unicode(self.team_profile)

class Invoice(models.Model):
	stripe_id = models.CharField(max_length=50)
	customer = models.ForeignKey(Customer)
	date = models.DateTimeField()
	amount = models.FloatField()
	payment_method = models.CharField(max_length=50)
	period_ending = models.DateTimeField()
	paid = models.BooleanField()

class Project(models.Model):
	creator = models.ForeignKey(UserProfile)
	team_profile = models.ForeignKey(TeamProfile, related_name='team_profile', null=True, blank=True)
	name = models.CharField(max_length=50)
	slug = models.SlugField(max_length=50)
	description = models.CharField (max_length=250, null=True, blank=True)
	public = models.BooleanField(default=True)
	license = models.ForeignKey(License, default=1)
	picture = models.ImageField(upload_to=repo_media_upload_location, null=True, blank=True)
	collaborators = models.ManyToManyField(Profile, related_name='collaborators', blank=True)
	created_at = models.DateTimeField()
	last_updated = models.DateTimeField(null=True, blank=True)
	active = models.BooleanField(default=True)
	parent = models.ForeignKey('self', related_name = 'parent_repo_in_repo', null=True, blank=True)
	head_sha1 = models.CharField(max_length=40, null=True, blank=True)

	def __unicode__(self):
		return unicode(self.name)

	class Meta:
		permissions = (
			("view_project", "Can see all project info"),
			("edit_project", "Can update project content"),
			("repo_project", "Can change admin settings for a project"),
		)
		unique_together = ('name', 'creator')

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		self.updated_at = timezone.now()
		super(Repository, self).save(*args, **kwargs)

	def get_absolute_url(self, branch_name='master', version_name='latest'):
		url = reverse("view_repo", kwargs={"profile_name": self.owner, "repo_name": self.slug, "branch_name": branch_name, "version_name": version_name})
		return url


