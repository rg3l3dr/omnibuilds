from django.shortcuts import render
from django.contrib.auth.models import User
from .forms import *
from omnibuilds.utils import get_mailchimp_api


# Create your views here.
def landing(request):
	if request.user.is_authenticated and (request.user.is_anonymous() is False):
		context = {}
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