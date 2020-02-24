from django.http import HttpResponse, Http404
from django.template import loader
from django.shortcuts import render, get_object_or_404, get_list_or_404

from .models import Person, Family

def index(request):
    return HttpResponse("Here is the familytree index.")

def family_index(request):
    family_list = Family.objects.order_by('-display_name')[:25]
    context = { 'family_list': family_list}
    return render(request, 'familytree/family_index.html', context)

def person_index(request):
    person_list = Person.objects.order_by('-display_name')[:25]
    context = { 'person_list': person_list}
    return render(request, 'familytree/person_index.html', context)

def person_detail(request, person_id):
    person = get_object_or_404(Person, pk=person_id)

    # @TODO: come back and fix for both parents- this way doesn't work (all end up 404)
    # right_list = get_list_or_404(Family, partner1=person_id)
    # left_list = get_list_or_404(Family, partner2=person_id)
    # families_made = right_list & left_list

    try:
        families_made = Family.objects.filter(partner1=person_id)
    except Family.DoesNotExist:
        families_made = None

    return render(request, 'familytree/person_detail.html', {'person': person, 'families_made': families_made})

def family_detail(request, family_id):
    family = get_object_or_404(Family, pk=family_id)

    try:
        kids = Person.objects.filter(origin_family=family_id)
    except Person.DoesNotExist:
        kids = None

    #
    #kids = get_list_or_404(Person, origin_family=family_id)
    return render(request, 'familytree/family_detail.html', {'family': family, 'kids': kids})


# def results(request, question_id):
#     response = "You're looking at the results of question %s."
#     return HttpResponse(response % question_id)
#
# def vote(request, question_id):
#     return HttpResponse("You're voting on question %s." % question_id)