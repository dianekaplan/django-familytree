
[BUILDING IN PROGRESS] Django family tree tool that can import data from a GEDCOM file (the 
common geneology standard used on sites like ancestry.com). 

**Basic family tree (import once from gedcom)**
Setup/data import: 
- Set environment variables (local in .bash_profile, staging/prod in heroku): 
export ENV_ROLE=development
export FAMILY_LOCAL_DB_PASS=[your local db password]
export EMAIL_HOST_PASSWORD=[your email host password]
ROOT_URL (temporary?)
SOURCE_DATABASE_PASSWORD
SECRET_KEY

- save gedcom file in: mysite/familytree/management/commands/gedcom_files
- from directory with manage.py, run: python3 manage.py importgedcom your_file.ged

By default, all of your person/family records will display to all users

**Add family branches**
Some relatives/users are only related to one part of the family, so I want to only show them people/images related to them.
Define family branches in the admin UI as a way of (a) sorting people for clearer display and (b) showing each user the people 
they're related to. I define 4 branches in my instance (one for each of my grandparents), which makes things easier to find: 
- people and family index pages show separate columns for each branch
- the 'family history' page shows separate sections for each branch
- the logged-in user only sees this and other content (family album, videos, etc) based on which branch(es) they're in.
Setup: in the admin area, add up to 4 branches, then specify which branch(es) apply for all the various records: 
people, family, images, and more. 

**To import multiple times from gedcom**
Background info about IDs: 
- In a gedcom file, the INDI values associate people and family records to each other. However, these are only internal 
to the specific file, and THESE IDs CAN CHANGE in subsequent gedcom exports from the same tool. 
- A combination of import scripts populate unique IDs for the families (following this convention: https://www.ged-gen.com/help/hlpmisc-number.html)
 and people ("gedcom_UUID"), which we then populate
in ancestry.com as an "also known as" fact, which maps to ALIA tag in gedcom file. 

**Detailed setup and usage notes**
https://github.com/dianekaplan/familytree-django