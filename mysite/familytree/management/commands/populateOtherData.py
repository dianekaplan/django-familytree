from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from ...models import User, Profile, Person, Branch
from django.core.management import call_command

class Command(BaseCommand):
    help = 'test- call other commands (internal use)'


    def handle(self, *args, **kwargs):

        #call_command('populateImageAssociations', 'images_people_family.csv')
        #call_command('populateNotes')
        #call_command('populateEasyTables')
       # call_command('sqlsequencereset', app_label='familytree')
        call_command('sqlsequencereset', 'familytree', no_color=True)
        #call_command('django-admin', 'sqlsequencereset', app_label='familytree')