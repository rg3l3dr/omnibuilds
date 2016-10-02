# from __future__ import unicode_literals

# from django.db import models

# """ Django.contrib.auth Models

# 	class User(models.Model):
# 		first_name = models.CharField(null=True, blank=True, max_length=30)
# 		last_name = models.CharField(null=True, blank=True, max_length=30)
# 		email = models.Emailfield(null=True, blank=True)
# 		password = models.HashField()
# 		groups = models.ManytoManyField(Group)
# 		user_permissions = models.ManytoManyField(Permission)
# 		is_staff = models.BooleanField()
# 		is_active = models.BooleanField()
# 		is_superuser = models.BooleanField()
# 		last_login = models.DateTimeField()
# 		date_joined = models.DateTimeField()

# 	class Permission(models.Model):
# 		name = models.CharField(max_length=255)
# 		content_type = models.ForeignKey(ContentType)
# 		codename = models.CharField(max_length=100)

# 	class Group(models.Model):
# 		name = models.CharField(max_length=80)
# 		permisssions = models.ManytoManyField(Permission)
# """

# # a newsletter subscription
# class SignUp(models.Model):

# # user invites friend onto site via email
# class Invite(models.Model):

# class Plan(models.Model):

# class Team(models.Model):
# 	name = models.CharField(max_length=30, unqiue=True)
# 	domain = models.SlugField(max_length=30, unique = True)
# 	leader = models.ForeignKey(User)
# 	plan = models.ForeignKey(Plan)
# 	public = models.BooleanField(default=True)
# 	about = models.TextField(null=True, blank=True)
# 	picture = models.ImageField()
# 	created_at = models.DateTimeField()
# 	active = models.BooleanField(default=True)

# 	def __unicode__(self):
#         return unicode(self.name)

#     def get_absolute_url(self):
#         url = reverse("view_team", kwargs={"team_name": self.slug})
#         return url

#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.name)
#         super(Profile, self).save(*args, **kwargs)

# 	# only checked if the team is private
# 	class Meta:
# 		permissions = (
# 			("view_team", "Can see all team info"),				# guests, read only and comments
# 			("edit_team", "Can edit any team info"),			# members, read/write, create/edit projects
# 			("team_admin", "Can change settings for a team"),	# leader, full admin access
# 		)

# # team leader invites teammate or guest onto team via email
# class TeamInvite(models.Model):

# class TeamMember(models.Model):
# 	team = models.ForeignKey(Team)
# 	user = models.ForeignKey(User)
# 	handle = models.CharField(max_length=30)

# class TeamProject(models.Model):
# 	team = models.ForeignKey(Team)
# 	creator = models.ForeignKey(TeamMember)
