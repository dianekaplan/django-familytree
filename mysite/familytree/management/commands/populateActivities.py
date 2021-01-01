from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from ...models import Person, Note, Family, User
from django.contrib.admin.models import LogEntry
from django.conf import settings
from django.utils.timezone import make_aware

class Command(BaseCommand):
    help = 'Migrates activities from previous database info django_admin_log (internal use)'

    settings.TIME_ZONE

    def make_log_entry(self, row_list):
        try:
            user_to_associate = User.objects.get(id=row_list[4])
            #parameters_dict['user_id'] = user_to_associate
        except:
            print(str(id=row_list[6]) + " doesn't match a user_id in our data")

        # parse the type of change (create or update) and asset (person, family, or note)
        action, type =row_list[3].split('_')
        action_flag = 2 if action=="updated" else 1
        display_value = ''

        if type =="person":
            content_type_id = 4
            try:
                person_to_associate = Person.objects.get(id=row_list[1])
            except:
                print(str(row_list[1]) + " doesn't match a person_id in our data. Here's the row data:" + str(row_list))
            else:
                display_value = person_to_associate.display_name
        if type =="family":
            content_type_id = 2
            try:
                family_to_associate = Family.objects.get(id=row_list[1])
            except:
                print(str(row_list[1]) + " doesn't match a family_id in our data. Here's the row data:" + str(row_list))
            else:
                display_value = family_to_associate.display_name
        if type =="note":
            content_type_id = 9
            try:
                note_to_associate = Note.objects.get(id=row_list[1])
            except:
                print(str(row_list[1]) + " doesn't match a note in our data. Here's the row data:" + str(row_list))
            else:
                display_value = "Note by: " + note_to_associate.author_name

        info_dict = {'action_time': make_aware(row_list[5]),'object_id':row_list[1], 'object_repr':display_value,
                     'action_flag':action_flag, 'change_message':"[change from old laravel site]", 'content_type_id':content_type_id,
                     'user_id':row_list[4]}

        (obj, created_bool) = LogEntry.objects.using('default').get_or_create(**info_dict)

    def handle(self, *args, **kwargs):

        with connections['source'].cursor() as cursor:
            cursor.execute('select * from activities')
            data = cursor.fetchall()

        # Add auth_user record
            for row in data:
                row_list = list(row)
                self.make_log_entry(row_list)
