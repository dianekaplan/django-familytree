from datetime import datetime

from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import Person, Family, Image, ImagePerson, Note , Branch, Profile, Video
from django.contrib.auth import logout
from django.conf import settings

media_server = settings.MEDIA_SERVER
today = datetime.now()  # used to get birthday_people and anniversary_couples

branch1_name = Branch.objects.filter(id=1)
branch2_name = Branch.objects.filter(id=2)
branch3_name = Branch.objects.filter(id=3)
branch4_name = Branch.objects.filter(id=4)
show_by_branch = True if branch1_name else False

def index(request):  #dashboard page
    user = request.user
    this_person = get_user_person(request.user).first()

    profile = Profile.objects.filter(user=user)
    accessible_branches = get_valid_branches(request)

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

    context = {'user': user, 'birthday_people': birthday_people,  'anniversary_couples': anniversary_couples,
               'latest_pics': latest_pics, 'user_person': this_person, 'profile': profile,
               'accessible_branches': accessible_branches,  'media_server': media_server
               }

    return render(request, 'familytree/dashboard.html', context )


def family_index(request):
    this_person = get_user_person(request.user).first()
    family_list = Family.objects.order_by('display_name')
    accessible_branches = get_valid_branches(request)

    # @@TODO: update so we can use branch1_name variables instead (tried but it's not working yet)
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
    # @@TODO: update so we can use branch1_name variables instead (tried but it's not working yet)
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
                'request_user': request.user,
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
        videos = Video.objects.filter(person=person)
    except Video.DoesNotExist:
        videos = None

    try:
        group_images = ImagePerson.objects.filter(person_id=person_id)
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

    return render(request, 'familytree/person_detail.html', {'person': person, 'families_made': families_made, 'origin_family': origin_family,
                                                        'images': images, 'group_images': group_images, 'notes': notes, 'videos': videos,
                                                        'featured_images': featured_images, 'user_person': user_person,
                                                        'media_server': media_server })


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
        images = Image.objects.filter(family_id=family_id)
    except Image.DoesNotExist:
        images = None

    return render(request, 'familytree/family_detail.html', {'family': family, 'kids': kids, 'notes': notes,
                                                             'featured_images': featured_images, 'icons': images,
                                                             'user_person': user_person, 'media_server': media_server})


def image_detail(request, image_id):
    user_person = get_user_person(request.user).first()
    image = get_object_or_404(Image, pk=image_id)

    this_image_person, this_image_family, image_people = Image.image_subjects(image)
    image_full_path = media_server + "/image/upload/r_20/" + image.big_name

    return render(request, 'familytree/image_detail.html', {'image': image, 'image_person': this_image_person,
                                                            'image_family': this_image_family,
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
    video = get_object_or_404(Image, pk=video_id)

    video_people = Video.video_subjects(video)

    return render(request, 'familytree/image_detail.html', {'video': video, 'video_people' : video_people,
                            'user_person': user_person, 'media_server': media_server})

def landing(request):
    landing_page_people = Person.objects.filter(show_on_landing_page=True)

    context = { 'landing_page_people': landing_page_people, 'media_server': media_server}
    return render(request, 'familytree/landing.html', context)

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

def logout(request):
    logout(request)
    return render(request, 'familytree/landing.html')
