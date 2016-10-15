# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-14 04:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('designer', '0002_auto_20161013_0442'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'permissions': (('view_profile', 'Can see all profile info'), ('edit_profile', 'Can edit any profile info'), ('profile_admin', 'Can change settings for a profile'))},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'permissions': (('view_repo', 'Can see all repo info'), ('edit_repo', 'Can update repo content'), ('repo_admin', 'Can change admin settings for a repo'))},
        ),
        migrations.AddField(
            model_name='project',
            name='collaborators',
            field=models.ManyToManyField(blank=True, related_name='collaborators', to='designer.Profile'),
        ),
        migrations.AlterField(
            model_name='project',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='designer.UserProfile'),
        ),
        migrations.RemoveField(
            model_name='project',
            name='team',
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together=set([('name', 'creator')]),
        ),
    ]
