
Django family tree tool that can import data from a GEDCOM file (the 
common geneology standard used on sites like ancestry.com), and allow you to: 
- create a family tree you can augment with pictures, video/audio clips, stories, and notes
- set up users with access to specific branches of the tree (so they see only the content for their own relatives)
- summarize 'family history' for each branch of the family, to help pull together narratives to orient your users

**Overview**
This tool provides a way to set up a more customized display for your family tree, pulling the people/families from your 
GEDCOM file to set up the structure (you can also add them one at a time using the django admin), but where you then add 
your own custom content and have control over the display. For now this assumes working knowledge of Django, as well as 
having some media server to host your images. The instance of my family tree runs on Heroku, using the Cloudinary plugin
to host images and video/audio files. 

**Determine what 'branches' to set up for your family**
Some relatives/users are only related to one part of the family, so I want to only show them people/images related to them.
Define family branches in the admin UI as a way of (a) sorting people for clearer display and (b) showing each user the people 
they're related to. I define 4 branches in my instance (one for each of my grandparents), which makes things easier to find: 
- people and family index pages show separate columns for each branch
- the 'family history' page shows separate sections for each branch
- the logged-in user only sees this and other content (family album, videos, etc) based on which branch(es) they're in.
Setup: in the admin area, add up to 4 branches, then specify which branch(es) apply for all the various records: 
people, family, images, and more. 

**Have a way to map these records to those on your ancestry tree**
After the initial GEDCOM import is done, you'll still be learning new things in your family tree and adding new people. 
You need a way to map a person's record in this tree with the one in ancestry, and unfortunately the GEDCOM format
doesn't provide unique IDs. This tool has scripts to generate unique IDs for every person, but we then need to add them 
in to the corresponding records in ancestry.com. (That way subsequent imports recognize which people are already there 
and don't need to be re-added).

**Requirements**
You'll need: 
- a place to host your website (I use Heroku)
- a database (I use postgres, via pgAdmin 4)
- a media server if you want to use images (I use the Cloudinary add-on for Heroku)
- an email host/account to send mails from (for password reset flow, etc)

**Detailed setup and usage notes**
https://github.com/dianekaplan/familytree-django/wiki