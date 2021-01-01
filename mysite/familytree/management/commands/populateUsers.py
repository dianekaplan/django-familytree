from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from ...models import User, Profile, Person, Branch


class Command(BaseCommand):
    help = 'Migrates user info from previous database(internal use)'

    def add_user(self, row_list):
            full_name = row_list[1]
            try:
                first_name, last_name = full_name.split(" ", 1)
            except:
                print("skipping junk user")

            else:
                # print("row_list[18] has: " + str(row_list[18]))
                # print("with make_aware, it has: " + str(make_aware(row_list[18])))
                auth_user_dict = {'id': row_list[0], 'password':row_list[3], 'last_login':row_list[6],
                              'is_superuser':row_list[5],'username': row_list[2], 'first_name':first_name, 'last_name':last_name,
                              'email': row_list[2],'is_active':row_list[9], 'date_joined':row_list[18]}

                # auth_user table has not null username, but I use email to log in- can just populate with that for now
                (obj, created_bool) = User.objects.using('default').get_or_create(**auth_user_dict)
                print("making user: " + str(full_name))

    def add_profile(self, row_list):
            profiles_dict = {'logins': row_list[7],'last_pestered':row_list[8], 'connection_notes':row_list[10],
                             'furthest_html':row_list[11],'shared_account':row_list[12]}
            try:
                user = User.objects.get(id=row_list[0])
            except:
                print(str(row_list[0]) + " DOESN'T MATCH USER_ID in our data")
            else:
                profiles_dict['user'] = user

                try:
                    person = Person.objects.get(id=row_list[4])
                except:
                    print(str(row_list[4]) + " doesn't match a person_id in our data")
                else:
                    profiles_dict['person'] = person
                    print("profiles_dict has: " + str(profiles_dict))
                    (obj, created_bool) = Profile.objects.using('default').get_or_create(**profiles_dict)

                    # Add profile branches
                    keem_access = row_list[13]
                    husband_access = row_list[14]
                    kemler_access = row_list[15]
                    kaplan_access = row_list[16]

                    if keem_access:
                        branch_to_associate = Branch.objects.get(id=1)
                        obj.branches.add(branch_to_associate)
                        obj.save()
                        print("Added " + branch_to_associate.display_name + " for: " + obj.person.display_name)

                    if husband_access:
                        branch_to_associate = Branch.objects.get(id=2)
                        obj.branches.add(branch_to_associate)
                        obj.save()
                        print("Added " + branch_to_associate.display_name + " for: " + obj.person.display_name)

                    if kemler_access:
                        branch_to_associate = Branch.objects.get(id=3)
                        obj.branches.add(branch_to_associate)
                        obj.save()
                        print("Added " + branch_to_associate.display_name + " for: " + obj.person.display_name)

                    if kaplan_access:
                        branch_to_associate = Branch.objects.get(id=4)
                        obj.branches.add(branch_to_associate)
                        obj.save()
                        print("Added " + branch_to_associate.display_name + " for: " + obj.person.display_name)


    def handle(self, *args, **kwargs):

        with connections['source'].cursor() as cursor:
            cursor.execute('select * from users')
            data = cursor.fetchall()

        # Add auth_user record
            for user_row in data:
                print(user_row)
                row_list = list(user_row)
                self.add_user(row_list)
                self.add_profile(row_list)
