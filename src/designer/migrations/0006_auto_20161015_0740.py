# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-15 07:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('designer', '0005_userprofile_public_name'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Plan',
            new_name='SubPlan',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='plan',
            new_name='subplan',
        ),
    ]
