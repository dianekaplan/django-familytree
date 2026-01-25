from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Orchestrates all important populate commands in the correct order"

    def handle(self, **options):
        """
        Runs the following commands in sequence:
        1. populateDirectFamilyNumbers
        2. populateUniqueIds
        3. populateBirthYear
        4. populateLivingBool

        Stops execution if populateDirectFamilyNumbers fails (ROOT_FAMILY not set/found).
        """

        # Step 1: populateDirectFamilyNumbers
        self.stdout.write(self.style.SUCCESS("\n=== Running populateDirectFamilyNumbers ==="))
        try:
            call_command("populateDirectFamilyNumbers")
        except CommandError as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Error: populateDirectFamilyNumbers failed. ROOT_FAMILY may not be set or found. "
                    f"Stopping execution.\n{str(e)}"
                )
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Unexpected error in populateDirectFamilyNumbers: {str(e)}\nStopping execution.")
            )
            return

        # Step 2: populateUniqueIds
        self.stdout.write(self.style.SUCCESS("\n=== Running populateUniqueIds ==="))
        try:
            call_command("populateUniqueIds")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"populateUniqueIds encountered an issue: {str(e)}"))
            # Continue execution despite warnings

        # Step 3: populateBirthYear
        self.stdout.write(self.style.SUCCESS("\n=== Running populateBirthYear ==="))
        try:
            call_command("populateBirthYear")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"populateBirthYear encountered an issue: {str(e)}"))
            # Continue execution despite warnings

        # Step 4: populateLivingBool
        self.stdout.write(self.style.SUCCESS("\n=== Running populateLivingBool ==="))
        try:
            call_command("populateLivingBool")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"populateLivingBool encountered an issue: {str(e)}"))
            # Continue execution despite warnings

        self.stdout.write(self.style.SUCCESS("\n=== All populate commands completed ==="))
