
Just a proof of concept to start, but this will be a django family tree tool that can import data from a GEDCOM file (the 
common geneology standard used on sites like ancestry.com). 

**Basic family tree (import once from gedcom)**
Setup/data import: 
- For local environment, update .bash_profile with: 
export ENV_ROLE=development
export FAMILY_LOCAL_DB_PASS=[your local password]

- save gedcom file in expected place (to start: mysite/familytree/management/commands/gedcom_files)
- run in directory with manage.py: python3 manage.py importgedcom your_file.ged

By default, all of your person/family records will display to all users

**Add family branches**
Some relatives/users are only related to one part of the family, so I want to only show them people/images related to them.
You can define family branches as a way of (a) sorting people for clearer display and (b) showing each user the people 
they're related to. I define 4 branches in my instance (one for each of my grandparents), which makes things easier to find: 
- people and family index pages show separate columns for each branch
- the 'family history' page shows separate sections for each branch
- the logged-in user only sees this and other content (family album, videos, etc) based on which branch(es) they're in.
Setup: in the admin area, add up to 4 branches, then you can specify which branch(es) apply for people, families, images, and more.

**To import multiple times from gedcom**
Background info about IDs: 
- In a gedcom file, the INDI values associate people and family records to each other. However, these are only internal 
to the specific file, and THESE IDs CAN CHANGE in subsequent gedcom exports from the same tool. 
- In the gedcom standard, the tag meant for unique ID is REFN. Unfortunately gedcom files exported from Ancestry.com do 
not offer a fact/field that uses this tag. 
- Therefore we can use the existing INDI values for a one-time gedcom import, and the person/family records in this family 
tree will use their own database IDs (for foreign key to associate pictures, notes, etc).  
- Then if we've added new people in ancestry.com and want to re-import an updated gedcom file, we need a workaround field 
to act as the unique ID. I'll add this value as "gedcom_UUID" in our person records, and as an "also known as" fact on ancestry.com, which maps to ALIA tag in gedcom file. 

Before subsequent update: 
- for each person, add unique field in person records (gedcom_UUID) and "also known as" fact on ancestry.com before exporting 
gedcom file. The convention I chose was to give each family a number like this: https://www.ged-gen.com/help/hlpmisc-number.html
Then each user ID gets an ID with the family number they connect with with a string of first names to get to them. 
For example a third cousin may have ID: 15NathanNoahMichaelMarc. Then a spouse who married in is that ID + SP, etc.

**Other usage notes**
- We'll default to showing a person's given name(s) and last name, but if you'd like to use some other nickname you can 
update "display_name" field. (We show that instead, if it's populated) 
