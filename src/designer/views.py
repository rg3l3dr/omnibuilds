from __future__ import division
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .forms import *
from .models import *
from omnibuilds.utils import get_mailchimp_api
from invitations.models import Invitation
from rest_framework import viewsets
from .serializers import *
import stripe

def get_user_profile(user_obj):
	if user_obj.is_authenticated and (user_obj.is_anonymous() is False):
		user = get_object_or_404(User, username=user_obj)
		user_profile = get_object_or_404(UserProfile, user=user)

		# next step is to account for user_profile vs team_profile

		return user_profile
	else:
		return None

def landing(request):
	if request.user.is_authenticated and (request.user.is_anonymous() is False):

		user_profile = get_user_profile(request.user)
		user_profile.data_percent = (user_profile.data / user_profile.data_cap) * 100

		context = {'user_profile': user_profile}
		return render(request, 'dashboard.html', context)


	if request.method=='POST':
		form=SignupForm(request.POST)

		print request.POST

		if form.is_valid():
			instance = form.save(commit=False)
			if request.POST['beta'] == 'True':
				instance.beta = True
			instance.save()

			m = get_mailchimp_api()
			email= {"email": instance.email}
			merge_vars={"FNAME": instance.first_name, "LNAME": instance.last_name}
			try:
				m.lists.subscribe(
					'26516eec38', 
					email,
					merge_vars, 
					double_optin=False, 
					update_existing=False, 
					send_welcome=True
					)

				print '%s has subscribed to newsletter!' % (instance.email)
			except Exception, e:
				print e
	else:
		form=SignupForm()	

	context={'form': form}
	return render(request, 'landing.html', context)

def invite(request):

	if request.method == 'POST':
		inviteform = InviteForm(request.POST)
		if inviteform.is_valid():
			email = inviteform.cleaned_data['email']
			invite = Invitation.create(email, inviter=request.user)
			invite.send_invitation(request)
	else:
		inviteform = InviteForm()

	context = {'inviteform': inviteform}
	return render(request, 'profile/invite.html', context)

def profile(request):

	user_profile = get_user_profile(request.user)
	edituserprofileform = EditUserProfileForm(request.POST or None, request.FILES or None, instance=user_profile)
	edituseraccountform = EditUserAccountForm(request.POST or None, instance=request.user)

	if request.method == 'POST':
		if request.POST.get("profile"):
			if user_profile.user.has_perm('designer.profile_admin', user_profile):
				if edituserprofileform.is_valid():
					instance = edituserprofileform.save(commit=False)
					instance.save()
					return redirect("profile")
			else:
				return HttpResponseForbidden()

		elif request.POST.get("account"):
			if user_profile.user.has_perm('designer.profile_admin', user_profile):
				if edituseraccountform.is_valid():
					instance = edituseraccountform.save(commit=False)
					instance.save()
					return redirect("profile")
			else:
				return HttpResponseForbidden()

		elif request.POST.get("stripeToken"):
			# Set your secret key: remember to change this to your live secret key in production
			# See your keys here: https://dashboard.stripe.com/account/apikeys
			stripe.api_key = "sk_test_uvOSw0wKosYSzUxJE8jrVBqb"

			# Get the credit card details submitted by the form
			token = request.POST['stripeToken']

			# Create a Customer
			customer = stripe.Customer.create(
			  source=token,
			  plan=1,
			  email=user_profile.user.email
			)

			user_profile.subplan_id = 2
			user_profile.save()


	context = {'edituserprofileform': edituserprofileform, 'edituseraccountform': edituseraccountform, 'user_profile': user_profile}
	return render(request, 'profile/profile_settings.html', context)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class SubPlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = SubPlan.objects.all()
    serializer_class = SubPlanSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class TeamProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TeamProfile.objects.all()
    serializer_class = TeamProfileSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer





