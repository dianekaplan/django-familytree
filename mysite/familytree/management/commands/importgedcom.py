from django.core.management.base import BaseCommand, CommandError
from ...models import Person, Family
from pathlib import Path

from sys import stdout
class Command(BaseCommand):
    help = 'Imports records from GEDCOM file'
    missing_args_message = 'Please specify GEDCOM file'

    def add_arguments(self, parser):
        parser.add_argument('file name', type=Path, help='Name of GEDCOM file to import from')

    def handle(self, *args, **kwargs):
        filename = kwargs['file name']

        # validate that the user gave file with extension ged
        if filename.suffix!= '.ged':
            raise CommandError('Please specify GEDCOM file, ex: myGedcom.ged')

        # Check that the file is there
        path = Path("familytree/management/commands/gedcom_files/")
        path_plus_file = path.joinpath(filename)

        if (path_plus_file.is_file()):
            stdout.write("The given file exists")
            file_contents = path_plus_file.read_text()
            file_contents_list = file_contents.split("/n")
            for line in file_contents_list:
                stdout.write(line)
        else:
            raise CommandError('That gedcom file does not exist in the expected directory')

        # read in the file

        # then I want to parse the file and do things with it


        # for poll_id in options['poll_ids']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     poll.opened = False
        #     poll.save()

        self.stdout.write(self.style.SUCCESS('You passed filename: ') + str(filename))
        #self.stdout.write(Path('path_plus_file.name: ' + str(path_plus_file)))

