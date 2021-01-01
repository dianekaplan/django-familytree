from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from ...models import User, Profile, Person, Branch
from django.core.management import call_command

class Command(BaseCommand):
    help = 'test- call other commands (internal use)'


    def handle(self, *args, **kwargs):
        print("CALLING populateImageAssociations images_people_family.csv")
        call_command('populateImageAssociations', 'images_people_family.csv')
        print("CALLING populateNotes")
        call_command('populateNotes')
        print("CALLING populateUsers")
        call_command('populateUsers')
        print("CALLING populateVideos")
        call_command('populateVideos')
        print("CALLING populateAudioFiles")
        call_command('populateAudioFiles')

        call_command('populateEasyTables')
        call_command('sqlsequencereset', 'familytree', no_color=True)
        call_command('sqlsequencereset', 'auth', no_color=True)