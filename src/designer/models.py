from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


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

# # a newsletter subscription
class Signup(models.Model):
	first_name = models.CharField(max_length=30, null=True, blank=True)
	last_name = models.CharField(max_length=30, null=True, blank=True)
	email = models.EmailField()
	beta = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

# # user invites friend onto site via email
# class Invite(models.Model):

# # team leader invites teammate or guest onto team via email
# class TeamInvite(models.Model):

class Plan(models.Model):
	name = models.CharField(max_length=30)
	description = models.TextField(null=True, blank=True)
	rate = models.IntegerField()

class Team(models.Model):
	name = models.CharField(max_length=30, unique=True)
	domain = models.SlugField(max_length=30, unique = True)
	leader = models.ForeignKey(User)
	plan = models.ForeignKey(Plan)
	public = models.BooleanField(default=True)
	about = models.TextField(null=True, blank=True)
	created_at = models.DateTimeField()
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return unicode(self.name)

	def get_absolute_url(self):
		url = reverse("view_team", kwargs={"team_name": self.slug})
		return url

	# def save(self, *args, **kwargs):
	#     self.slug = slugify(self.name)
	#     super(Team, self).save(*args, **kwargs)

	# only checked if the team is private
	class Meta:
		permissions = (
			("view_team", "Can see all team info"),				# guests, read only and comments
			("edit_team", "Can edit any team info"),			# members, read/write, create/edit projects
			("team_admin", "Can change settings for a team"),	# leader, full admin access
		)

class Member(models.Model):
	team = models.ForeignKey(Team)
	user = models.ForeignKey(User)
	handle = models.CharField(max_length=30)
	slug = models.SlugField(max_length=30)

	def __unicode__(self):
		return unicode(self.handle)

	# def get_absolute_url(self):
	#     url = reverse("view_member", kwargs={"member_name": self.slug})
	#     return url

	def save(self, *args, **kwargs):
		self.slug = slugify(self.handle)
		super(Member, self).save(*args, **kwargs)


# class TeamProject(models.Model):
# 	team = models.ForeignKey(Team)
# 	creator = models.ForeignKey(TeamMember)
