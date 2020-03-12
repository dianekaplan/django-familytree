from datetime import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import Person, Family, Image, ImagePerson, Note, Branch

today = datetime.now() # used to get birthday_people and anniversary_couples
branch1_name = Branch.objects.filter(id=1)
branch2_name = Branch.objects.filter(id=2)
branch3_name = Branch.objects.filter(id=3)
branch4_name = Branch.objects.filter(id=4)
show_by_branch = True  # default this to False, but set to true if you've set families

def index(request):
    user = request.user

    try:
        birthday_people = Person.objects.filter(birthdate__month=today.month).order_by('birthdate__day')
    except Person.DoesNotExist:
        birthday_people = None

    try:
        anniversary_couples = Family.objects.filter(marriage_date__month=today.month).order_by('marriage_date__day')
    except Family.DoesNotExist:
        anniversary_couples = None

    try:
        latest_pics = Image.objects.all().order_by('-id')[:10]
    except Image.DoesNotExist:
        latest_pics = None

    context = {'user': user, 'birthday_people': birthday_people,  'anniversary_couples': anniversary_couples, 'latest_pics': latest_pics}

    return render(request, 'familytree/dashboard.html', context )


def family_index(request):
    family_list = Family.objects.order_by('display_name')

    branch1_families = Family.objects.filter(branches__display_name__contains="Keem")
    branch2_families = Family.objects.filter(branches__display_name__contains="Husband")
    branch3_families = Family.objects.filter(branches__display_name__contains="Kemler")
    branch4_families = Family.objects.filter(branches__display_name__contains="Kobrin")

    context = { 'family_list': family_list, 'branch1_families': branch1_families, 'branch2_families': branch2_families,
                'branch3_families': branch3_families, 'branch4_families': branch4_families, 'branch1_name': branch1_name,
                'branch2_name': branch2_name, 'branch3_name': branch3_name, 'branch4_name': branch4_name, 'show_by_branch': show_by_branch}

    return render(request, 'familytree/family_index.html', context)


def person_index(request):
    # to start we'll assume up to 4 branches, gets ids 1-4, entering names manually
    # @TODO: make this grab them dynamically instead
    branch1_people = Person.objects.filter(branches__display_name__contains="Keem")
    branch2_people = Person.objects.filter(branches__display_name__contains="Husband")
    branch3_people = Person.objects.filter(branches__display_name__contains="Kemler")
    branch4_people = Person.objects.filter(branches__display_name__contains="Kobrin")

    person_list = Person.objects.order_by('display_name') # add this to limit list displayed: [:125]
    context = { 'person_list': person_list, 'branch1_people': branch1_people, 'branch2_people': branch2_people,
                'branch3_people': branch3_people, 'branch4_people': branch4_people, 'branch1_name': branch1_name,
                'branch2_name': branch2_name, 'branch3_name': branch3_name, 'branch4_name': branch4_name, 'show_by_branch': show_by_branch}
    return render(request, 'familytree/person_index.html', context)


def person_detail(request, person_id):
    person = get_object_or_404(Person, pk=person_id)

    try:
        wife_of = Family.objects.filter(wife=person_id)
        husband_of = Family.objects.filter(husband=person_id)
        families_made = wife_of | husband_of
    except Family.DoesNotExist:
        families_made = None

    try:
        images = Image.objects.filter(person_id=person_id)
    except Image.DoesNotExist:
        images = None

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

    return render(request, 'familytree/person_detail.html', {'person': person, 'families_made': families_made,
                                                             'images': images, 'group_images': group_images, 'notes': notes,
                                                             'featured_images': featured_images})


def family_detail(request, family_id):
    family = get_object_or_404(Family, pk=family_id)

    try:
        kids = Person.objects.filter(origin_family=family_id)
    except Person.DoesNotExist:
        kids = None

    try:
        notes = Note.objects.filter(family_id=family_id)
    except ImagePerson.DoesNotExist:
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
                                                             'featured_images': featured_images, 'icons': images})


def image_detail(request, image_id):
    image = get_object_or_404(Image, pk=image_id)

    this_image_person, this_image_family, image_people = Image.image_subjects(image)

    return render(request, 'familytree/image_detail.html', {'image': image, 'image_person': this_image_person,
                                                            'image_family': this_image_family,
                                                            'image_people' : image_people
                                                            })


def image_index(request):
    image_list = Image.objects.order_by('year') # add this to limit list displayed: [:125]
    context = { 'image_list': image_list}
    return render(request, 'familytree/image_index.html', context)
