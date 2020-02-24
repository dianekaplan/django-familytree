
Just a proof of concept to start, but this will be a django family tree tool that can import data from a GEDCOM file (the common geneology standard used on sites like ancestry.com). 

Setup/data import: 
- add unique field in ancestry.com before exporting gedcom file
- save gedcom file in expected place (to start: mysite/familytree/management/commands/gedcom_files)
- run in directory with manage.py: python3 manage.py importgedcom your_file.ged
