from __future__ import division
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .forms import *
from .models import *
from omnibuilds.utils import get_mailchimp_api
from invitations.models import Invitation
from notifications.models import Notification
from rest_framework import viewsets
from .serializers import *
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import datetime
from django.http import HttpResponse

def get_user_profile(user_obj):
	if user_obj.is_authenticated and (user_obj.is_anonymous() is False):
		user = get_object_or_404(User, username=user_obj)
		user_profile = get_object_or_404(UserProfile, user=user)

		# next step is to account for user_profile vs team_profile

		return user_profile
	else:
		return None

""" Gravatar Workflow --later

    1. All you need for a gravatar is the email, which you get on signup/create account
    2. Now every time they login you will need to check their gravatar (this can be done client side)
    3. Should the user have the ability to override their gravatar profile with something else?

    -> User creates an account
    -> Attempt to pull gravatar profile
        -> Success: use gravatar profile by default
        -> None: use default profile (used updates their own profile)
    -> Gravatar profile displays in the following:
        -> navbar profile dropdown
        -> profile dashboard
        -> profile settings
        -> any time an avatar is referecned in a team or project
    -> Would it make sense to store this as a vue component ???

    Every time they login the request should be made from gravatar

"""

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

	user_profile = get_user_profile(request.user)
	invitations = Invitation.objects.filter(inviter=request.user.id)
	user_profile.accepted_invites = [invite for invite in invitations if invite.accepted]

	for invite in user_profile.accepted_invites:
		try:
			User.objects.get(email = invite.email)
			invite.joined = True
		except User.DoesNotExist:
			invite.joined = False

	user_profile.pending_invites = [invite for invite in invitations if not invite.accepted]

	for invite in user_profile.pending_invites:
		invite.expired = invite.key_expired

	if request.method == 'POST':
		if inviteform.is_valid():
			email = inviteform.cleaned_data['email']
			invite = Invitation.create(email, inviter=request.user)
			invite.send_invitation(request)
	else:
		inviteform = InviteForm()

	context = {'inviteform': inviteform, 'user_profile': user_profile}
	return render(request, 'profile/invite.html', context)

def my_notifications(request):

	user_profile = get_user_profile(request.user)	
	notifications = Notification.objects.filter(recipient = request.user)

	for notification in notifications:
		notification.description = unicode(notification)

	context = {'user_profile': user_profile, 'notifications': notifications}

	if request.method == 'POST':
		body = json.loads(request.body)
		for item in body:
			pk = item['id']
			notification = get_object_or_404(Notification, id = pk)
			if item['action'] == 'unread':
				notification.unread = True 
			else: 
				notification.unread = False
			notification.save()

	return render(request, 'profile/messages.html', context)

@require_http_methods(["POST"])
@csrf_exempt
def stripe_webhook(request):
  # Retrieve the request's body and parse it as JSON
  event = json.loads(request.body)
  print 'Stripe webhook received'
  print event['type']

  if event['type'] == 'invoice.payment_succeeded':
  	print 'detected payment succeeded event'
  	#update the customer object
  	customer_id = event['data']['object']['customer']
  	customer = Customer.objects.get(stripe_customer_id = customer_id)
  	date = datetime.datetime.fromtimestamp(float(event['data']['object']['date']))
  	end_date = datetime.datetime.fromtimestamp(float(event['data']['object']['period_end']))
  	customer.next_payment = end_date
  	payment_method = '%s ending in %s' % (customer.card_brand, customer.card_last4)
  	
  	if customer.failed_count:
  		# retrieve and update the invoice
  		invoice = Invoice.objects.filter(customer = customer)[-1]
  		invoice.paid = True
  		invoice.payment_method = payment_method
  		invoice.date = date
  		invoice.period_ending = end_date
  		invoice.save()

  	else:
	  	# create the new invoice
	  	Invoice.objects.create(
	  		stripe_id = event['data']['object']['id'],
	  		customer = customer,
			date = date,
			amount = event['data']['object']['total'],
			payment_method = payment_method,
			period_ending = end_date,
			paid = True
	  		)

  	# update the customer
  	customer.failed_count = 0
  	customer.save()

  	# stripe sends successful payment email to customer

  elif event['type'] == 'invoice.payment_failed':
  	# get the customer object
  	customer_id = event['data']['object']['customer']
  	customer = Customer.objects.get(stripe_customer_id = customer_id)
  	date = datetime.datetime.fromtimestamp(float(event['data']['object']['date']))
  	end_date = datetime.datetime.fromtimestamp(float(event['data']['object']['period_end']))
  	customer.next_payment = end_date
  	payment_method = '%s ending in %s' % (customer.card_brand, customer.card_last4)

  	if not customer.failed_count:
  		# create the invoice
	  	Invoice.objects.create(
	  		stripe_id = event['data']['object']['id'],
	  		customer = customer,
			date = date,
			amount = event['data']['object']['total'],
			payment_method = payment_method,
			period_ending = end_date,
			paid = False
	  		)

  	# update the customer
  	customer.failed_count += 1
  	# send notification to user

  	if customer.failed_count == 1:
	  	notify.send(recipient=customer.user_profile.user, verb='Your monthly subscription charge has failed, please update your credit card information.  We will make two more attempts before deactivating your private account.')
	  	# send email to user ...

	elif customer.failed_count == 2:
		notify.send(recipient=customer.user_profile.user, verb='Your monthly subscription charge has failed, please update your credit card information.  We will make one more attempt before deactivating your private account.')
	  	# send email to user ...

  	if customer.failed_count >= 3:
  		# remove accesss to private repositories
  		# send notification/email to user 
  		notify.send(recipient=customer.user_profile.user, verb='Your private account has been deactivated due to three failed payment attempts.')

  	customer.save()

  return HttpResponse(status=200)

def profile(request):

	""" Subscription Workflow

	Remaining Steps 

	->  Handle inactive customer records properly

	"""

	user_profile = get_user_profile(request.user)
	customers = Customer.objects.filter(user_profile=user_profile)
	invoices = Invoice.objects.filter(customer__in=customers)
	user_profile.invoices = invoices
	
	try:
		user_profile.customer = Customer.objects.get(user_profile=user_profile, active=True)
	except Customer.DoesNotExist:
		user_profile.customer = False

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
					user_profile.name = instance.username
					user_profile.save()
					return redirect("profile")
			else:
				return HttpResponseForbidden()

		elif request.POST.get("stripeToken"):

			print 'Received a stripe token'

			# Set your secret key: remember to change this to your live secret key in production
			# See your keys here: https://dashboard.stripe.com/account/apikeys
			stripe.api_key = "sk_test_uvOSw0wKosYSzUxJE8jrVBqb"

			# Get the credit card details submitted by the form
			token = request.POST['stripeToken']
			print "Token is %s" % (token)

			if user_profile.customer:  # updating billing info for an existing customer
				customer = stripe.Customer.retrieve(user_profile.customer.stripe_customer_id)
				customer.source = token
				customer.save()
				customer = stripe.Customer.retrieve(user_profile.customer.stripe_customer_id)
				card = customer.sources.data[0]

				django_customer = get_object_or_404(Customer, id=user_profile.customer.id)
				django_customer.card_brand = card.brand
				django_customer.card_last4 = card.last4
				django_customer.card_exp_month = card.exp_month
				django_customer.card_exp_year = card.exp_year
				django_customer.save()

				user_profile.customer = django_customer

			else: # creating a new customer

				# Create a Customer
				customer = stripe.Customer.create(
				  source=token,
				  plan=1,
				  email=user_profile.user.email
				)

				card = customer.sources.data[0]
				subscription = customer.subscriptions.data[0]
				next_payment = datetime.datetime.fromtimestamp(subscription.current_period_end)

				# create a the omnibuilds customer (for records)
				Customer.objects.create(
					user_profile = user_profile,
					sub_plan_id = 2,
					stripe_customer_id = customer.id,
					card_brand = card.brand,
					card_last4 = card.last4,
					card_exp_month = card.exp_month,
					card_exp_year = card.exp_year,
					next_payment = next_payment,
					active = True,
					failed_count = 0,
					)

				print "***New Customer Created in profile (view)***"

				# update the user_profile based on new plan
				user_profile.subplan_id = 2
				user_profile.data_cap += 5000000000
				user_profile.save()

		elif request.POST.get("status"):

			print 'received a status message'
			# cancelling a customer account

			# cancel the subscription on stripe
			stripe.api_key = "sk_test_uvOSw0wKosYSzUxJE8jrVBqb"
			customer = stripe.Customer.retrieve(user_profile.customer.stripe_customer_id)
			subscription_id = customer.subscriptions.data[0].id
			subscription = stripe.Subscription.retrieve(subscription_id)
			subscription.delete()

			# deactivate the customer record
			user_profile.customer.active = False
			user_profile.customer.save()

			# change the plan for this profile
			user_profile.subplan_id = 1
			# reduce the data plan
			user_profile.data_cap -= 5000
			# remove access to private repos???
			user_profile.save()

	context = {'edituserprofileform': edituserprofileform, 'edituseraccountform': edituseraccountform, 'user_profile': user_profile}
	

	return render(request, 'profile/profile_settings.html', context)

"""Django REST Framework viewsets
"""

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

class CustomerViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows users to be viewed or edited.
	"""
	queryset = Customer.objects.all()
	serializer_class = CustomerSerializer

class ProjectViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows users to be viewed or edited.
	"""
	queryset = Project.objects.all()
	serializer_class = ProjectSerializer

class InvitationViewSet(viewsets.ModelViewSet):

	queryset = Invitation.objects.all()
	serializer_class = InvitationSerializer





