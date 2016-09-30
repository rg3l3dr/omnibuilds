from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabvenv import virtualenv

"""
All commands must be run from src

*** Rolling Deployment ***

Commit to GitHub
fab push:commit='my update'

Deploy to Test
fab deploy_gunicorn -i /Users/jeremiahwagstaff/Desktop/Development/Keys/cafabra.pem -H ubuntu@ec2-52-40-250-232.us-west-2.compute.amazonaws.com

-- deprecated --
fab deploy_nginx -i /Users/jeremiahwagstaff/Desktop/Development/Keys/cafabra.pem -H ubuntu@ec2-.us-west-2.compute.amazonaws.com

Deploy to Prod
fab deploy_gunicorn -i /Users/jeremiahwagstaff/Desktop/Development/Keys/cafabra.pem -H ubuntu@ec2-52-40-122-199.us-west-2.compute.amazonaws.com

-- deprecated --
fab deploy_nginx -i /Users/jeremiahwagstaff/Desktop/Development/Keys/cafabra.pem -H ubuntu@ec2-52-39-60-239.us-west-2.compute.amazonaws.com

*** Force Deployment ***

fab deploy_all:commit='my hotfix'

"""

def push(commit):
	local('echo "yes" | python manage.py collectstatic')
	local ("python manage.py makemigrations")
	local ('python manage.py migrate')
	with lcd ('/home/ubuntu/omnibuilds/omnibuilds'):
		local ('pip freeze > requirements.txt')
		local ('git add .')
		local ('git commit -m "%s"' % commit)
		local ('git push')

def ezpush(commit):
	with lcd ('/home/ubuntu/omnibuilds/omnibuilds'):
		local ('git add .')
		local ('git commit -m "%s"' % commit)
		local ('git push origin master')

