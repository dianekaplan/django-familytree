from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from ...models import User, Profile, Person, Branch
from django.core.management import call_command

class Command(BaseCommand):
    help = 'populate person and family data (internal use)'


    def handle(self, *args, **kwargs):
        call_command('populateDisplayNames')
        call_command('populatePeopleFamilies', 'People_families.csv')
        call_command('populateBranchAssociations', 'families_spouses_branches.csv')