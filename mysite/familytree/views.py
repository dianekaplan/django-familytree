from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib.admin.models import LogEntry, ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.conf import settings

from .models import Person, Family, Image, ImagePerson, Note , Branch, Profile, Video, Story, PersonStory, Audiofile

media_server = settings.MEDIA_SERVER
root_url = settings.ROOT_URL
today = datetime.now()
guest_user_anniversary_cutoff = today.date() - relativedelta(years=50)
month_ago_date = today.date() - relativedelta(days=30)
laravel_site_creation = datetime.strptime('2015-12-01', '%Y-%m-%d').date()
django_site_creation = datetime.strptime('2021-07-14', '%Y-%m-%d').date()

branch1_name = Branch.objects.filter(id=1)
branch2_name = Branch.objects.filter(id=2)
branch3_name = Branch.objects.filter(id=3)
branch4_name = Branch.objects.filter(id=4)
show_by_branch = True if branch1_name else False
login_url = '/familytree/landing/'
newest_generation_for_guest = 13 # guest users will not see any generations newer (higher) than this

# pass style class name for index pages based on user's number of columns
branch_classes = {
    1: 'one_branch_display',
    2: 'two_branch_display',
    4: 'four_branch_display'
}


@login_required(login_url=login_url)
def index(request):  # dashboard page
    user = request.user
    profile = get_display_profile(request).first()
    this_person = get_profile_person(profile)
    user_is_guest = profile.guest_user
    accessible_branches = get_valid_branches(request)
    browser = request.user_agent.browser.family

    # only include additions or updates, for family, person, story
    display_update_types = [2, 4, 5]
    display_action_types = [1, 2]
    recent_logentries = LogEntry.objects.filter(content_type_id__in=display_update_types,
                                                action_flag__in=display_action_types).order_by('-id')[:5]

    # get list of latest updates
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

    # get list of people with birthdays this month
    birthday_people_combined = Person.objects.none()
    try:
        for branch in accessible_branches:
            these_birthday_people = Person.objects.filter(birthdate__month=today.month).\
                filter(branches__display_name__contains=branch.display_name)
            birthday_people_combined = birthday_people_combined | these_birthday_people
        birthday_people_sorted = birthday_people_combined.order_by('birthdate__day').distinct()
    except Person.DoesNotExist:
        birthday_people = None

    if user_is_guest:
        birthday_people = [x for x in birthday_people if x.living is False]

    # get list of families with anniversaries this month
    try:
        anniversary_couples = Family.objects.filter(marriage_date__month=today.month, divorced=False).order_by('marriage_date__day')
    except Family.DoesNotExist:
        anniversary_couples = None

    if user_is_guest:
        anniversary_couples = [x for x in anniversary_couples if x.marriage_date < guest_user_anniversary_cutoff]

    # get list of recent images
    image_list = Image.objects.none()
    try:
        for branch in accessible_branches:
            latest_pics = Image.objects.filter(branches__display_name__contains=branch.display_name).order_by('-id')
            image_list = image_list | latest_pics
        combined_image_list = image_list.order_by('-id').distinct()[:10]
    except Image.DoesNotExist:
        combined_image_list = None

    # get list of recent videos
    video_list = Video.objects.none()
    try:
        for branch in accessible_branches:
            latest_videos = Video.objects.filter(branches__display_name__contains=branch.display_name).order_by('-id')
            video_list = video_list | latest_videos
        combined_video_list = video_list.order_by('-id').distinct()[:3]
    except Video.DoesNotExist:
        combined_video_list = None

    # get list of people with a birthday today
    try:
        today_birthday = Person.objects.filter(birthdate__month=today.month).filter(birthdate__day=today.day).order_by('birthdate__year')
    except Person.DoesNotExist:
        today_birthday = None

    # get list of recent stories
    try:
        latest_stories = Story.objects.all().order_by('-id')[:5]
    except Story.DoesNotExist:
        latest_stories = None

    context = {'user': user, 'birthday_people': birthday_people_sorted,  'anniversary_couples': anniversary_couples,
               'show_book': False, 'latest_pics': combined_image_list, 'latest_videos': combined_video_list, 'user_person': this_person,
               'profile': profile, 'accessible_branches': accessible_branches, 'today_birthday': today_birthday,
               'media_server': media_server, 'recent_logentries': recent_logentries, 'recent_updates': recent_updates,
               'user_is_guest': user_is_guest, 'browser': browser, 'latest_stories': latest_stories}

    return render(request, 'familytree/dashboard.html', context)


@login_required(login_url=login_url)
def family_index(request):
    profile = get_display_profile(request).first()
    this_person = get_profile_person(profile)
    family_list = Family.objects.order_by('display_name')
    accessible_branches = get_valid_branches(request)
    user_is_guest = Profile.objects.get(user=request.user).guest_user
    existing_branches_list = list(Branch.objects.all())

    # @@TODO: specific to 4-branch setup, will want to be flexible for others
    branch1_families = Family.objects.filter(branches__display_name__contains=existing_branches_list[0],
                                             show_on_branch_view=True, reviewed=True).order_by('branch_seq', 'marriage_date')

    branch2_families = Family.objects.filter(branches__display_name__contains=existing_branches_list[1],
                                             show_on_branch_view=True, reviewed=True).order_by('branch_seq', 'marriage_date')

    branch3_families = Family.objects.filter(branches__display_name__contains=existing_branches_list[2],
                                             show_on_branch_view=True, reviewed=True).order_by('branch_seq', 'marriage_date')

    branch4_families = Family.objects.filter(branches__display_name__contains=existing_branches_list[3],
                                             show_on_branch_view=True, reviewed=True).order_by('branch_seq', 'marriage_date')

    context = { 'family_list': family_list,
                'branch1_families': branch1_families, 'branch2_families': branch2_families,
                'branch3_families': branch3_families, 'branch4_families': branch4_families, 'branch1_name': branch1_name,
                'branch2_name': branch2_name, 'branch3_name': branch3_name, 'branch4_name': branch4_name,
                'show_by_branch': show_by_branch, 'accessible_branches': accessible_branches, 'user_person': this_person,
                'media_server': media_server, 'branch_class': branch_classes[len(accessible_branches)],
                'user_is_guest': user_is_guest, 'newest_generation_for_guest': newest_generation_for_guest}

    return render(request, 'familytree/family_index.html', context)


@login_required(login_url=login_url)
def person_index(request):
    accessible_branches = get_valid_branches(request)
    profile = get_display_profile(request).first()
    user_person = get_profile_person(profile)
    user_is_guest = Profile.objects.get(user=request.user).guest_user
    existing_branches_list = list(Branch.objects.all())

    # @@TODO: specific to 4-branch setup, will want to be flexible for others
    branch1_people = Person.objects.filter(branches__display_name__contains=existing_branches_list[0], hidden=False,
                                           reviewed=True).order_by('last', 'first')
    branch2_people = Person.objects.filter(branches__display_name__contains=existing_branches_list[1], hidden=False,
                                           reviewed=True).order_by('last', 'first')
    branch3_people = Person.objects.filter(branches__display_name__contains=existing_branches_list[2], hidden=False,
                                           reviewed=True).order_by('last', 'first')
    branch4_people = Person.objects.filter(branches__display_name__contains=existing_branches_list[3], hidden=False,
                                           reviewed=True).order_by('last', 'first')

    # person_list is used if there aren't defined branches yet
    person_list = Person.objects.order_by('display_name') # add this to limit list displayed: [:125]
    context = { 'person_list': person_list,
                'branch1_people': branch1_people, 'branch2_people': branch2_people,
                'branch3_people': branch3_people, 'branch4_people': branch4_people, 'branch1_name': branch1_name,
                'branch2_name': branch2_name, 'branch3_name': branch3_name, 'branch4_name': branch4_name,
                'show_by_branch': show_by_branch, 'accessible_branches':accessible_branches,
                'request_user': request.user, 'show_book': True, 'user_is_guest': user_is_guest,
                'user_person': user_person, 'media_server': media_server,
                'branch_class': branch_classes[len(accessible_branches)]
                }
    return render(request, 'familytree/person_index.html', context)


@login_required(login_url=login_url)
def person_detail(request, person_id):
    profile = get_display_profile(request).first()
    user_person = get_profile_person(profile)
    person = get_object_or_404(Person, pk=person_id)
    user_is_guest = Profile.objects.get(user=request.user).guest_user
    browser = request.user_agent.browser.family

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
                            'user_person': user_person, 'stories': stories, 'media_server': media_server, 'browser': browser,
                                                             'user_is_guest': user_is_guest })


@login_required(login_url=login_url)
def family_detail(request, family_id):
    family = get_object_or_404(Family, pk=family_id)
    profile = get_display_profile(request).first()
    user_person = get_profile_person(profile)
    user_is_guest = Profile.objects.get(user=request.user).guest_user

    try:
        kids = Person.objects.filter(family_id=family_id).order_by('birthyear', 'sibling_seq','id')
    except Person.DoesNotExist:
        kids = None

    try:
        notes = Note.objects.filter(family_id=family_id)
    except Note.DoesNotExist:
        notes = None

    try:
        featured_images = Image.objects.filter(family_id=family_id).order_by('id') & Image.objects.filter(featured=1)
    except Image.DoesNotExist:
        featured_images = None

    try:
        images = Image.objects.filter(family_id=family_id).order_by('year')
    except Image.DoesNotExist:
        images = None

    return render(request, 'familytree/family_detail.html', {'family': family, 'kids': kids, 'notes': notes,'show_book': True,
                                                             'featured_images': featured_images, 'images': images,
                                                             'user_person': user_person, 'media_server': media_server,
                                                             'user_is_guest': user_is_guest })


@login_required(login_url=login_url)
def image_detail(request, image_id):
    profile = get_display_profile(request).first()
    user_person = get_profile_person(profile)
    image = get_object_or_404(Image, pk=image_id)
    user_is_guest = Profile.objects.get(user=request.user).guest_user

    this_image_person, this_image_family, image_people = Image.image_subjects(image)
    image_full_path = media_server + "/image/upload/r_20/" + image.big_name

    return render(request, 'familytree/image_detail.html', {'image': image, 'image_person': this_image_person,
                                                            'image_family': this_image_family, 'show_book': False,
                                                            'image_people': image_people, 'user_person': user_person,
                                                            'image_full_path': image_full_path,
                                                            'media_server': media_server, 'user_is_guest': user_is_guest
                                                            })


@login_required(login_url=login_url)
def image_index(request):
    profile = get_display_profile(request).first()
    user_person = get_profile_person(profile)
    accessible_branches = get_valid_branches(request)
    image_list = Image.objects.none()

    for branch in accessible_branches:
        name = branch.display_name
        image_list = image_list.union(Image.objects.filter(branches__display_name__contains=name).order_by('year'))
    sorted_list = image_list.order_by('year')

    context = {'image_list': sorted_list, 'accessible_branches': accessible_branches, 'branch2_name': branch2_name,
                'user_person': user_person, 'media_server' : media_server}
    return render(request, 'familytree/image_index.html', context)


@login_required(login_url=login_url)
def video_detail(request, video_id):
    profile = get_display_profile(request).first()
    user_person = get_profile_person(profile)
    video = get_object_or_404(Video, pk=video_id)
    video_people = Video.video_subjects(video)
    user_is_guest = Profile.objects.get(user=request.user).guest_user

    cloud_name = media_server.split("/")[3]
    public_id = video.name
    params = "cloud_name=" + cloud_name + "&public_id=" + public_id + "&vpv=1.4.0";
    video_url = "https://player.cloudinary.com/embed/?" + params;

    return render(request, 'familytree/video_detail.html', {'video': video,'video_people': video_people,
                                                            'user_person': user_person, 'media_server': media_server,
                                                            'video_url': video_url, 'show_book': True, 'user_is_guest': user_is_guest})


@login_required(login_url=login_url)
def video_index(request):
    profile = get_display_profile(request).first()
    user_person = get_profile_person(profile)
    accessible_branches = get_valid_branches(request)
    existing_branches = Branch.objects.all()
    video_list = Video.objects.none()
    browser = request.user_agent.browser.family

    for branch in existing_branches:
        if branch in accessible_branches:
            name = branch.display_name
            video_list = video_list.union(Video.objects.filter(branches__display_name__contains=name).order_by('year'))
    sorted_list = video_list.order_by('year')

    context = { 'video_list': sorted_list, 'accessible_branches': accessible_branches, 'branch2_name': branch2_name,
                'user_person': user_person, 'media_server' : media_server, 'browser': browser}
    return render(request, 'familytree/video_index.html', context)


@login_required(login_url=login_url)
def story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)

    return render(request, 'familytree/story.html', {'story': story,'media_server': media_server})


@login_required(login_url=login_url)
def outline(request):
    profile = get_display_profile(request).first()
    this_person = get_profile_person(profile)
    accessible_branches = get_valid_branches(request)
    existing_branches = Branch.objects.all()
    user_is_guest = Profile.objects.get(user=request.user).guest_user

    users_original_families = {}  # Dictionary with entries [branch name]: [original families in that branch]
    total_results = {}  # giant dictionary for all descendants
    total_results_html = {}

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
                this_family_results = get_descendants(family, user_is_guest)
                this_branch_results.append(this_family_results)
            total_results[name] = this_branch_results

            this_branch_html = make_list_into_html(this_branch_results)
            total_results_html[name] = this_branch_html

    context = {'accessible_branches': accessible_branches, 'user_person': this_person,
               'family_dict': users_original_families, 'media_server': media_server,'show_book': True,
               'total_results': total_results, 'total_results_html': total_results_html}

    return render(request, 'familytree/outline.html', context)


def make_list_into_html(list):
    result = ''

    for item in list:
        if type(item) == Person:
            name = item.display_name
            path = root_url + "/people/" + str(item.id)
            link = '<li><a href="' + path + '">' + name + '</a></li>'
            result += link
        elif type(item) == Family:
            name = item.display_name
            path = root_url + "/families/" + str(item.id)
            link = '<ul><li><a href="' + path + '">' + name + '</a></li>'
            result += link
        else:
            html = make_list_into_html(item)
            result += html
            result += '</ul>'
    return result


def landing(request):
    landing_page_people = Person.objects.filter(living=False, show_on_landing_page=True).order_by('last', 'first')

    context = {'landing_page_people': landing_page_people, 'media_server': media_server}
    return render(request, 'familytree/landing.html', context)


@login_required(login_url=login_url)
def history(request):
    user = request.user
    profile = get_display_profile(request).first()
    this_person = get_profile_person(profile)
    accessible_branches = get_valid_branches(request)

    context = {'accessible_branches': accessible_branches, 'user_person': this_person,
                'media_server': media_server,'profile': profile}
    return render(request, 'familytree/history.html', context)


def logout(request):
    logout(request)
    return render(request, 'familytree/landing.html')


def get_valid_branches(request):
    profile = get_display_profile(request)
    accessible_branches = Branch.objects.filter(profile__in=profile)
    return accessible_branches


# typically we'll use the display for the logged-in-user, but superusers can view as other profiles
def get_display_profile(request):
    user = request.user
    profile = Profile.objects.filter(user=user)
    # if it's a superuser, also check for show_profile parameter
    if request.user.is_superuser:
        show_profile = request.GET.get('show_profile', None)
        if show_profile:
            profile = Profile.objects.filter(id=int(show_profile))
            print("viewing as profile: ", profile)
    return profile


def get_profile_person(profile):
    try:
        this_user_person = profile.person
    except Profile.DoesNotExist:
        this_user_person = None
    return this_user_person


def get_descendants(family, user_is_guest, results=None):
    these_results = [family]
    kids = None

    try:
        kids = Person.objects.filter(family=family)
    except:
        pass
    else:
        if kids:
            for kid in kids:
                if not user_is_guest or not kid.living:
                    these_results.append(kid)
                    families_made = None
                    if kid.sex == 'F':
                        families_made = Family.objects.filter(wife=kid)
                    if kid.sex == 'M':
                        families_made = Family.objects.filter(husband=kid)
                    if families_made:
                        for new_family in families_made:
                            next_results = get_descendants(new_family, user_is_guest, these_results)
                            these_results.extend([next_results])
    return these_results

@login_required(login_url=login_url)
def account(request):
    profile = get_display_profile(request).first()
    this_person = get_profile_person(profile)
    accessible_branches = get_valid_branches(request)

    context = {'accessible_branches': accessible_branches, 'user_person': this_person,
                'media_server': media_server,}

    return render(request, 'familytree/account.html', context)

# These metrics are specific to my usage/history
@login_required(login_url=login_url)
def user_metrics(request):
    profile = get_display_profile(request).first()
    this_person = get_profile_person(profile)
    accessible_branches = get_valid_branches(request)
    profiles = Profile.objects.all()
    existing_branches_list = list(Branch.objects.all())

    last_login_never = [x for x in profiles if not x.last_login()]
    last_login_past_month = [x for x in profiles if x.last_login() and x.last_login().date() > month_ago_date]

    last_login_old_site_only = [x for x in profiles if x.last_login() and x.last_login().date() < laravel_site_creation]
    last_login_laravel_site = [x for x in profiles if x.last_login() and laravel_site_creation < x.last_login().date() <
                               django_site_creation]
    last_login_django_site = [x for x in profiles if x.last_login() and x.last_login().date() >= django_site_creation]

    profiles_who_made_notes = [x for x in profiles if x.notes_written()]

    branch1_users = Profile.objects.filter(branches__display_name__contains=existing_branches_list[0])
    branch2_users = Profile.objects.filter(branches__display_name__contains=existing_branches_list[1])
    branch3_users = Profile.objects.filter(branches__display_name__contains=existing_branches_list[2])
    branch4_users = Profile.objects.filter(branches__display_name__contains=existing_branches_list[3])

    context = {'accessible_branches': accessible_branches, 'user_person': this_person,
                'profiles': profiles, 'last_login_never': last_login_never, 'last_login_past_month': last_login_past_month,
               'last_login_old_site_only': last_login_old_site_only, 'profiles_who_made_notes': profiles_who_made_notes,
               'last_login_laravel_site': last_login_laravel_site, 'last_login_django_site': last_login_django_site,
               'branch1_users': branch1_users, 'branch2_users': branch2_users, 'branch3_users': branch3_users,
               'branch4_users': branch4_users, 'existing_branches_list': existing_branches_list
               }

    return render(request, 'familytree/user_metrics.html', context)
