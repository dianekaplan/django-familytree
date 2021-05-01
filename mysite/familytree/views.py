from datetime import datetime

from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.admin.models import LogEntry, ContentType

from .models import Person, Family, Image, ImagePerson, Note , Branch, Profile, Video, Story, PersonStory, Audiofile
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.conf import settings

media_server = settings.MEDIA_SERVER
today = datetime.now()  # used to get birthday_people and anniversary_couples

branch1_name = Branch.objects.filter(id=1)
branch2_name = Branch.objects.filter(id=2)
branch3_name = Branch.objects.filter(id=3)
branch4_name = Branch.objects.filter(id=4)
show_by_branch = True if branch1_name else False

def index(request):  # dashboard page
    user = request.user
    this_person = get_user_person(request.user).first()
    profile = Profile.objects.filter(user=user)
    accessible_branches = get_valid_branches(request)

    # only include additions or updates, for family, person, story
    display_update_types = [2, 4, 5]
    display_action_types = [1, 2]
    recent_logentries = LogEntry.objects.filter(content_type_id__in= display_update_types,
                                                action_flag__in=display_action_types).order_by('-id')[:5]

    recent_updates = []
    for update in recent_logentries:
        update_author = User.objects.get(username=update.user)
        user_profile = Profile.objects.get(user=update_author)
        user_person = Person.objects.get(id=user_profile.person_id)  # @TODO: can I consolidate these steps?
        updated_person = None

        if update.content_type_id == 4:
            updated_person = Person.objects.get(id=update.object_id)

        content_type = str(ContentType.objects.get(id=update.content_type_id)).replace("familytree | ","")
        change_type = "added" if update.action_flag==1 else "updated"
        combination = [update, user_person, content_type, change_type, updated_person]
        recent_updates.append(combination)

    try:
        birthday_people = Person.objects.filter(birthdate__month=today.month).order_by('birthdate__day')
    except Person.DoesNotExist:
        birthday_people = None

    try:
        anniversary_couples = Family.objects.filter(marriage_date__month=today.month, divorced=False).order_by('marriage_date__day')
    except Family.DoesNotExist:
        anniversary_couples = None

    try:
        latest_pics = Image.objects.all().order_by('-id')[:10]
    except Image.DoesNotExist:
        latest_pics = None

    try:
        latest_videos = Video.objects.all().order_by('-id')[:3]
    except Video.DoesNotExist:
        latest_videos = None

    try:
        today_birthday = Person.objects.filter(birthdate__month=today.month).filter(birthdate__day=today.day).order_by('birthdate__year')
    except Person.DoesNotExist:
        today_birthday = None

    context = {'user': user, 'birthday_people': birthday_people,  'anniversary_couples': anniversary_couples, 'show_book': False,
               'latest_pics': latest_pics, 'latest_videos': latest_videos, 'user_person': this_person, 'profile': profile,
               'accessible_branches': accessible_branches, 'today_birthday': today_birthday, 'media_server': media_server,
               'recent_logentries': recent_logentries, 'recent_updates':recent_updates}

    return render(request, 'familytree/dashboard.html', context )


def family_index(request):
    this_person = get_user_person(request.user).first()
    family_list = Family.objects.order_by('display_name')
    accessible_branches = get_valid_branches(request)

    # @@TODO: update so we can use branch1_name variables like outline_branch_partials view has
    branch1_families = Family.objects.filter(branches__display_name__contains="Keem",
                                             show_on_branch_view=True).order_by('branch_seq', 'marriage_date')
    branch2_families = Family.objects.filter(branches__display_name__contains="Husband",
                                             show_on_branch_view=True).order_by('branch_seq', 'marriage_date')
    branch3_families = Family.objects.filter(branches__display_name__contains="Kemler",
                                             show_on_branch_view=True).order_by('branch_seq', 'marriage_date')
    branch4_families = Family.objects.filter(branches__display_name__contains="Kobrin",
                                             show_on_branch_view=True).order_by('branch_seq', 'marriage_date')

    context = { 'family_list': family_list,
                'branch1_families': branch1_families, 'branch2_families': branch2_families,
                'branch3_families': branch3_families, 'branch4_families': branch4_families, 'branch1_name': branch1_name,
                'branch2_name': branch2_name, 'branch3_name': branch3_name, 'branch4_name': branch4_name,
                'show_by_branch': show_by_branch, 'accessible_branches': accessible_branches, 'user_person': this_person,
                'media_server': media_server}

    return render(request, 'familytree/family_index.html', context)


def person_index(request):
    accessible_branches = get_valid_branches(request)
    this_person = get_user_person(request.user).first()

    # to start we'll assume up to 4 branches, gets ids 1-4, entering names manually
    # @@TODO: update so we can use branch1_name variables like outline_branch_partials view has
    branch1_people = Person.objects.filter(branches__display_name__contains="Keem", hidden=False).order_by('last', 'first')
    branch2_people = Person.objects.filter(branches__display_name__contains="Husband", hidden=False).order_by('last', 'first')
    branch3_people = Person.objects.filter(branches__display_name__contains="Kemler", hidden=False).order_by('last', 'first')
    branch4_people = Person.objects.filter(branches__display_name__contains="Kobrin", hidden=False).order_by('last', 'first')

    person_list = Person.objects.order_by('display_name') # add this to limit list displayed: [:125]
    context = { 'person_list': person_list,
                'branch1_people': branch1_people, 'branch2_people': branch2_people,
                'branch3_people': branch3_people, 'branch4_people': branch4_people, 'branch1_name': branch1_name,
                'branch2_name': branch2_name, 'branch3_name': branch3_name, 'branch4_name': branch4_name,
                'show_by_branch': show_by_branch, 'accessible_branches':accessible_branches,
                'request_user': request.user, 'show_book': True,
                'user_person': this_person, 'media_server': media_server
                }
    return render(request, 'familytree/person_index.html', context)


def person_detail(request, person_id):
    user_person = get_user_person(request.user).first()
    person = get_object_or_404(Person, pk=person_id)

    try:
        wife_of = Family.objects.filter(wife=person_id)
        husband_of = Family.objects.filter(husband=person_id)
        families_made = wife_of | husband_of
    except Family.DoesNotExist:
        families_made = None

    try:
        origin_family = person.family
    except Family.DoesNotExist:
        origin_family = None

    try:
        images = Image.objects.filter(person_id=person_id).order_by('year')
    except Image.DoesNotExist:
        images = None

    try:
        person_story_records = PersonStory.objects.filter(person_id=person_id)
    except PersonStory.DoesNotExist:
        person_story_records = None

    if person_story_records:
        stories = set()
        for record in person_story_records:
            this_story = Story.objects.get(id=record.story_id)
            stories.add(this_story)
    else:
        stories = None

    try:
        videos = Video.objects.filter(person=person).order_by('year')
    except Video.DoesNotExist:
        videos = None

    try:
        group_images = ImagePerson.objects.filter(person_id=person_id).order_by('image__year')
    except ImagePerson.DoesNotExist:
        group_images = None

    try:
        notes = Note.objects.filter(person_id=person_id)
    except ImagePerson.DoesNotExist:
        notes = None

    try:
        featured_images = Image.objects.filter(person_id=person_id) & Image.objects.filter(featured=1)
    except Image.DoesNotExist:
        featured_images = None

    try:
        audio_files = Audiofile.objects.filter(person=person)
    except Audiofile.DoesNotExist:
        audio_files = None

    return render(request, 'familytree/person_detail.html', {'person': person, 'families_made': families_made,
                            'origin_family': origin_family, 'images': images, 'group_images': group_images,
                            'notes': notes, 'videos': videos, 'featured_images': featured_images,'audio_files': audio_files,
                            'user_person': user_person, 'stories': stories, 'media_server': media_server })


def family_detail(request, family_id):
    family = get_object_or_404(Family, pk=family_id)
    user_person = get_user_person(request.user).first()

    try:
        kids = Person.objects.filter(family_id=family_id).order_by('birthyear', 'sibling_seq','id')
    except Person.DoesNotExist:
        kids = None

    try:
        notes = Note.objects.filter(family_id=family_id)
    except Note.DoesNotExist:
        notes = None

    try:
        featured_images = Image.objects.filter(family_id=family_id) & Image.objects.filter(featured=1)
    except Image.DoesNotExist:
        featured_images = None

    try:
        images = Image.objects.filter(family_id=family_id).order_by('year')
    except Image.DoesNotExist:
        images = None

    return render(request, 'familytree/family_detail.html', {'family': family, 'kids': kids, 'notes': notes,'show_book': True,
                                                             'featured_images': featured_images, 'images': images,
                                                             'user_person': user_person, 'media_server': media_server})


def image_detail(request, image_id):
    user_person = get_user_person(request.user).first()
    image = get_object_or_404(Image, pk=image_id)

    this_image_person, this_image_family, image_people = Image.image_subjects(image)
    image_full_path = media_server + "/image/upload/r_20/" + image.big_name

    return render(request, 'familytree/image_detail.html', {'image': image, 'image_person': this_image_person,
                                                            'image_family': this_image_family, 'show_book': False,
                                                            'image_people' : image_people, 'user_person': user_person,
                                                            'image_full_path' : image_full_path, 'media_server' : media_server
                                                            })


def image_index(request):
    user_person = get_user_person(request.user).first()
    accessible_branches = get_valid_branches(request)
    existing_branches = Branch.objects.all()
    image_list = Image.objects.none()

    for branch in existing_branches:
        if branch in accessible_branches:
            name = branch.display_name
            image_list = image_list.union(Image.objects.filter(branches__display_name__contains=name).order_by('year'))
    sorted_list = image_list.order_by('year')

    context = { 'image_list': sorted_list, 'accessible_branches': accessible_branches, 'branch2_name': branch2_name,
                'user_person': user_person, 'media_server' : media_server}
    return render(request, 'familytree/image_index.html', context)


def video_detail(request, video_id):
    user_person = get_user_person(request.user).first()
    video = get_object_or_404(Video, pk=video_id)
    video_people = Video.video_subjects(video)

    cloud_name = media_server.split("/")[3]
    public_id = video.name
    params = "cloud_name=" + cloud_name + "&public_id=" + public_id + "&vpv=1.4.0";
    video_url = "https://player.cloudinary.com/embed/?" + params;

    return render(request, 'familytree/video_detail.html', {'video': video,'video_people': video_people,
                                                            'user_person': user_person, 'media_server': media_server,
                                                            'video_url': video_url, 'show_book': True})


def video_index(request):
    user_person = get_user_person(request.user).first()
    accessible_branches = get_valid_branches(request)
    existing_branches = Branch.objects.all()
    video_list = Video.objects.none()

    for branch in existing_branches:
        if branch in accessible_branches:
            name = branch.display_name
            video_list = video_list.union(Video.objects.filter(branches__display_name__contains=name).order_by('year'))
    sorted_list = video_list.order_by('year')

    context = { 'video_list': sorted_list, 'accessible_branches': accessible_branches, 'branch2_name': branch2_name,
                'user_person': user_person, 'media_server' : media_server}
    return render(request, 'familytree/video_index.html', context)


def story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)

    return render(request, 'familytree/story.html', {'story': story,'media_server': media_server})


def outline(request):
    this_person = get_user_person(request.user).first()
    accessible_branches = get_valid_branches(request)
    existing_branches = Branch.objects.all()

    users_original_families = {}  # Dictionary with entries [branch name]: [original families in that branch]
    total_results = {}  # giant dictionary for all descendants

    for branch in existing_branches:
        # For each branch this user has access for, we'll loop through the original families and:
        # 1) make the dictionary of original families by branch
        # 2) make the dictionary of descendants by branch

        if branch in accessible_branches:
            name = branch.display_name
            this_branch_results = []

            # make the dictionary of original families by branch
            orig_family_list = Family.objects.filter(branches__display_name__contains=name, original_family=True)
            users_original_families[name] = orig_family_list

            # make the dictionary of descendants by branch
            for family in orig_family_list:
                this_family_results = get_descendants(family)
                # print("OUTLINE HAS: " + str(this_family_results))
                this_branch_results.append(this_family_results)
            total_results[name] = this_branch_results

    # make_html_for_branch_outline(this_branch_results[0])

    context = {'accessible_branches': accessible_branches, 'user_person': this_person,
               'family_dict': users_original_families, 'media_server': media_server,'show_book': True,
               'chunk_view': "familytree/outline_family_chunk.html", 'total_results': total_results}

    return render(request, 'familytree/outline.html', context)


def landing(request):
    landing_page_people = Person.objects.filter(show_on_landing_page=True)

    context = { 'landing_page_people': landing_page_people, 'media_server': media_server}
    return render(request, 'familytree/landing.html', context)

def history(request):
    this_person = get_user_person(request.user).first()
    accessible_branches = get_valid_branches(request)

    context = {'accessible_branches': accessible_branches, 'user_person': this_person,
                'media_server': media_server,}

    return render(request, 'familytree/history.html', context)


def logout(request):
    logout(request)
    return render(request, 'familytree/landing.html')


def get_valid_branches(request):
    user = request.user
    profile = Profile.objects.filter(user=user)
    accessible_branches = Branch.objects.filter(profile__in=profile)
    return accessible_branches


def get_user_person(user):
    try:
        this_user_person = Person.objects.filter(profile__user_id=user)
    except Profile.DoesNotExist:
        this_user_person = None
    return this_user_person


def get_descendants(family, results=None):
    these_results = [family]
    kids = None

    try:
        kids = Person.objects.filter(family=family)
    except:
        pass
    else:
        if kids:
            for kid in kids:
                these_results.append(kid)
                families_made = None
                if kid.sex == 'F':
                    families_made = Family.objects.filter(wife=kid)
                if kid.sex == 'M':
                    families_made = Family.objects.filter(husband=kid)
                if families_made:
                    for new_family in families_made:
                        next_results = get_descendants(new_family, these_results)
                        these_results.extend([next_results])
    return these_results
