from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.admin.models import ADDITION, CHANGE, ContentType, LogEntry
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

# for receiver function to get album data
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from pytz import timezone

from .forms import EditPersonForm, NoteForm
from .models import (
    Audiofile,
    Branch,
    Family,
    FamilyStory,
    Image,
    ImagePerson,
    Note,
    Person,
    PersonStory,
    Profile,
    Story,
    Video,
)

media_server = settings.MEDIA_SERVER
LARAVEL_SITE_CREATION = settings.LARAVEL_SITE_CREATION
DJANGO_SITE_CREATION = settings.DJANGO_SITE_CREATION
NEWEST_GENERATION_FOR_GUEST = (
    settings.NEWEST_GENERATION_FOR_GUEST
)  # guest users only see generations older than this
root_url = settings.ROOT_URL

# @@TODO: this is specific to a 4-branch setup. Make it more flexible to handle other numbers of branches.
branch1_name = Branch.objects.filter(id=1)
branch2_name = Branch.objects.filter(id=2)
branch3_name = Branch.objects.filter(id=3)
branch4_name = Branch.objects.filter(id=4)
show_by_branch = True if branch1_name else False
login_url = "/familytree/landing/"
existing_branches_list = list(Branch.objects.all())
branch_count = len(existing_branches_list)



def get_branch_class(accessible_branches, request): 
    # pass style class name for index pages based on user's number of columns
    branch_classes = {
    1: "one_branch_display",
    2: "two_branch_display",
    4: "four_branch_display",
    }
    result = branch_classes[accessible_branches]

    show_mobile = request.user_agent.is_mobile or request.GET.get("show_mobile")
    if show_mobile: 
        result = "mobile_index_page_display"

    return result



@login_required(login_url=login_url)
def index(request):  # dashboard page
    profile = get_display_profile(request).first()
    user_is_guest = profile.guest_user
    accessible_branches = get_valid_branches(request)
    browser = request.user_agent.browser.family
    show_mobile = request.user_agent.is_mobile or request.GET.get("show_mobile")
    today = get_now_for_user(profile.timezone)
    guest_user_anniversary_cutoff = today.date() - relativedelta(years=50)
    picture_limit = 5 if show_mobile else 10

    template = (
        "familytree/dashboard_mobile.html"
        if show_mobile
        else "familytree/dashboard.html"
    )

    # only include additions or updates, for family, person, story, notes
    display_action_types = [1, 2]  # added, updated
    display_update_types = [2, 4, 5, 9]
    recent_logentries = LogEntry.objects.filter(
        content_type_id__in=display_update_types, action_flag__in=display_action_types
    ).order_by("-id")[:5]

    # get list of latest updates
    recent_updates = []
    for update in recent_logentries:
        update_author = update.user
        user_person = Profile.objects.get(user=update_author).person
        updated_person = None
        updated_story = None

        if update.content_type_id == 4:  # Person update
            updated_person = Person.objects.get(id=update.object_id)
        
        if update.content_type_id == 5:  # Story update (including association with person/family)
            updated_story = Story.objects.get(id=update.object_id)

        content_type = str(ContentType.objects.get(id=update.content_type_id)).replace(
            "familytree | ", ""
        )
        change_type = "added" if update.action_flag == 1 else "updated"
        combination = [update, user_person, content_type, change_type, updated_person, updated_story ]
        recent_updates.append(combination)

    # get list of people with birthdays this month
    birthday_people = Person.objects.none()
    birthday_people_combined = Person.objects.none()
    try:
        for branch in accessible_branches:
            these_birthday_people = Person.objects.filter(
                birthdate__month=today.month
            ).filter(branches__display_name__contains=branch.display_name)
            birthday_people_combined = birthday_people_combined | these_birthday_people
        birthday_people_sorted = birthday_people_combined.order_by(
            "birthdate__day"
        ).distinct()
    except Person.DoesNotExist:
        birthday_people = None

    if user_is_guest:
        birthday_people = [x for x in birthday_people if x.living is False]

    # get list of families with anniversaries this month
    anniversary_list = Family.objects.none()
    try:
        for branch in accessible_branches:
            this_branch_anniversary = (
                Family.objects.filter(marriage_date__month=today.month)
                .filter(
                    branches__display_name__contains=branch.display_name, divorced=False
                )
                .order_by("marriage_date__day")
            )
            anniversary_list = anniversary_list | this_branch_anniversary
        anniversary_couples = anniversary_list.order_by("marriage_date__day").distinct()
    except Family.DoesNotExist:
        anniversary_couples = False

    if user_is_guest:
        anniversary_couples = [
            x
            for x in anniversary_couples
            if x.marriage_date < guest_user_anniversary_cutoff
        ]

    # get list of recent images
    image_list = Image.objects.none()
    try:
        for branch in accessible_branches:
            latest_pics = Image.objects.filter(
                branches__display_name__contains=branch.display_name
            ).order_by("-id")
            image_list = image_list | latest_pics
        combined_image_list = image_list.order_by("-id").distinct()[:picture_limit]
    except Image.DoesNotExist:
        combined_image_list = None

    # get list of recent videos
    video_list = Video.objects.none()
    try:
        for branch in accessible_branches:
            latest_videos = Video.objects.filter(
                branches__display_name__contains=branch.display_name
            ).order_by("-id")
            video_list = video_list | latest_videos
        combined_video_list = video_list.order_by("-id").distinct()[:3]
    except Video.DoesNotExist:
        combined_video_list = None

    # get list of people with a birthday today
    today_birthday = [x for x in birthday_people_sorted if x.birthdate.day == today.day]

    # get list of recent stories
    story_list = Story.objects.none()
    try:
        for branch in accessible_branches:
            this_branch_stories = (
                Story.objects.filter(
                    branches__display_name__contains=branch.display_name
                )
                .filter(dashboard_feature=True)
                .order_by("-id")
            )
            story_list = story_list | this_branch_stories
        combined_story_list = story_list.order_by("-id").distinct()[:10]
    except Story.DoesNotExist:
        combined_story_list = None

    context = {
        "user": profile.user,
        "birthday_people": birthday_people_sorted,
        "anniversary_couples": anniversary_couples,
        "show_book": False,
        "latest_pics": combined_image_list,
        "latest_videos": combined_video_list,
        "user_person": profile.person,
        "profile": profile,
        "accessible_branches": accessible_branches,
        "today_birthday": today_birthday,
        "media_server": media_server,
        "recent_logentries": recent_logentries,
        "recent_updates": recent_updates,
        "user_is_guest": user_is_guest,
        "browser": browser,
        "latest_stories": combined_story_list,
    }

    return render(request, template, context)


@login_required(login_url=login_url)
def family_index(request):
    profile = get_display_profile(request).first()
    family_list = Family.objects.order_by("display_name")
    accessible_branches = get_valid_branches(request)
    user_is_guest = Profile.objects.get(user=request.user).guest_user

    if branch_count > 0:
        branch1_families = set_branch_families(existing_branches_list, 0)
    else:
        branch1_families = None

    if branch_count > 1:
        branch2_families = set_branch_families(existing_branches_list, 1)
    else:
        branch2_families = None

    if branch_count > 2:
        branch3_families = set_branch_families(existing_branches_list, 2)
    else:
        branch3_families = None

    if branch_count > 3:
        branch4_families = set_branch_families(existing_branches_list, 3)
    else:
        branch4_families = None

    context = {
        "family_list": family_list,
        "branch1_families": branch1_families,
        "branch2_families": branch2_families,
        "branch3_families": branch3_families,
        "branch4_families": branch4_families,
        "branch1_name": branch1_name,
        "branch2_name": branch2_name,
        "branch3_name": branch3_name,
        "branch4_name": branch4_name,
        "show_by_branch": show_by_branch,
        "accessible_branches": accessible_branches,
        "user_person": profile.person,
        "media_server": media_server,
        "branch_class": get_branch_class(len(accessible_branches), request),
        "user_is_guest": user_is_guest,
        "newest_generation_for_guest": NEWEST_GENERATION_FOR_GUEST,
        "user": profile.user,
    }

    return render(request, "familytree/family_index.html", context)


def set_branch_families(existing_branches_list, branch_int):
    families = Family.objects.filter(
        branches__display_name__contains=existing_branches_list[branch_int],
        show_on_branch_view=True,
        reviewed=True,
    ).order_by("branch_seq", "marriage_date")
    return families


def set_branch_stories(existing_branches_list, branch_int):
    stories = Story.objects.filter(
        branches__display_name__contains=existing_branches_list[branch_int],
        dashboard_feature=True,
    ).order_by("intro")
    return stories



@login_required(login_url=login_url)
def person_index(request):
    accessible_branches = get_valid_branches(request)
    profile = get_display_profile(request).first()
    user_is_guest = profile.guest_user

    if branch_count > 0:
        branch1_people = set_branch_people(existing_branches_list, 0)
    else:
        branch1_people = None

    if branch_count > 1:
        branch2_people = set_branch_people(existing_branches_list, 1)
    else:
        branch2_people = None

    if branch_count > 2:
        branch3_people = set_branch_people(existing_branches_list, 2)
    else:
        branch3_people = None

    if branch_count > 3:
        branch4_people = set_branch_people(existing_branches_list, 3)
    else:
        branch4_people = None

    # person_list is used if there aren't defined branches yet
    person_list = Person.objects.order_by("display_name")
    context = {
        "person_list": person_list,
        "branch1_people": branch1_people,
        "branch2_people": branch2_people,
        "branch3_people": branch3_people,
        "branch4_people": branch4_people,
        "branch1_name": branch1_name,
        "branch2_name": branch2_name,
        "branch3_name": branch3_name,
        "branch4_name": branch4_name,
        "show_by_branch": show_by_branch,
        "accessible_branches": accessible_branches,
        "request_user": request.user,
        "show_book": True,
        "user_is_guest": user_is_guest,
        "user_person": profile.person,
        "media_server": media_server,
        "user": profile.user,
        "branch_class": get_branch_class(len(accessible_branches), request),
    }
    return render(request, "familytree/person_index.html", context)


def set_branch_people(existing_branches_list, int):
    people = Person.objects.filter(
        branches__display_name__contains=existing_branches_list[int],
        hidden=False,
        reviewed=True,
    ).order_by("last", "first")
    return people


@login_required(login_url=login_url)
def person_detail(request, person_id):
    profile = get_display_profile(request).first()
    person = get_object_or_404(Person, pk=person_id)
    user_is_guest = profile.guest_user
    user_is_limited = profile.limited
    browser = request.user_agent.browser.family

    families_made = person.families_made()
    group_images = person.group_images()

    try:
        origin_family = person.family
    except Family.DoesNotExist:
        origin_family = None

    try:
        images = Image.objects.filter(person_id=person_id).order_by("year")
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
        videos = Video.objects.filter(person=person).order_by("year")
    except Video.DoesNotExist:
        videos = None

    try:
        notes = Note.objects.filter(person_id=person_id)
    except ImagePerson.DoesNotExist:
        notes = None

    try:
        featured_images = Image.objects.filter(
            person_id=person_id
        ) & Image.objects.filter(featured=1)
    except Image.DoesNotExist:
        featured_images = None

    try:
        audio_files = Audiofile.objects.filter(person=person)
    except Audiofile.DoesNotExist:
        audio_files = None

    return render(
        request,
        "familytree/person_detail.html",
        {
            "person": person,
            "families_made": families_made,
            "origin_family": origin_family,
            "images": images,
            "group_images": group_images,
            "notes": notes,
            "videos": videos,
            "featured_images": featured_images,
            "audio_files": audio_files,
            "user_person": profile.person,
            "stories": stories,
            "media_server": media_server,
            "browser": browser,
            "user": profile.user,
            "user_is_guest": user_is_guest,
            "user_is_limited": user_is_limited,
        },
    )


@login_required(login_url=login_url)
def add_note(request, object_id, object_type):
    profile = get_display_profile(request).first()
    note_form = NoteForm(request.POST)
    template_name = None
    editing_user = profile.user

    context = {
        "user_person": profile.person,
        "media_server": media_server,
        "note_form": note_form,
        "editing_user": editing_user,
    }

    if object_type == "person":
        template_name = "familytree/add_person_note.html"
        person = get_object_or_404(Person, pk=object_id)  # person note is about
        context["person"] = person
        page_name = "person_detail"

    if object_type == "family":
        template_name = "familytree/add_family_note.html"
        family = get_object_or_404(Family, pk=object_id)  # family note is about
        context["family"] = family
        page_name = "family_detail"

    if request.method == "POST":
        if note_form.is_valid():

            # make django_admin_log entry
            LogEntry.objects.log_action(
                user_id=editing_user.id,
                content_type_id=ContentType.objects.get_for_model(Note).pk,
                object_id=(str(object_type) + ":" + str(object_id)),
                object_repr=note_form["body"].value(),
                action_flag=ADDITION,
                change_message="Added note",
            )

            note_form.save()
            return redirect(page_name, object_id)

    if request.method == "GET":
        return render(request, template_name, context)


@login_required(login_url=login_url)
def edit_person(request, person_id):
    template_name = "familytree/edit_person.html"
    profile = get_display_profile(request).first()
    editing_user = profile.user
    person = get_object_or_404(
        Person, pk=person_id
    )  # person whose info will be updated
    person_edit_form = EditPersonForm(request.POST, instance=person)

    context = {
        "person": person,
        "editing_user": editing_user,
        "media_server": media_server,
        "form": person_edit_form,
    }

    if request.method == "POST":
        if person_edit_form.is_valid():
            # send an email to the site admin
            email_data = {"user": editing_user, "person": person}
            from_email = settings.ADMIN_EMAIL_SEND_FROM
            recipient_list = [settings.ADMIN_EMAIL_ADDRESS]
            subject = render_to_string(
                template_name="familytree/email/person_edit_subject.txt"
            )
            html_message = render_to_string(
                "familytree/email/person_edit_message.html", email_data
            )
            send_mail(
                subject, html_message, from_email, recipient_list, fail_silently=False
            )

            # make django_admin_log entry
            LogEntry.objects.log_action(
                user_id=editing_user.id,
                content_type_id=ContentType.objects.get_for_model(person).pk,
                object_id=person.id,
                object_repr=person.display_name,
                action_flag=CHANGE,
            )

            # make the edit to the person
            person_edit_form.save()

            return redirect("person_detail", person_id=person.id)
        else:
            print("FORM NOT VALID")
        return redirect("person_detail", person_id=person.id)

    if request.method == "GET":
        return render(request, template_name, context)


@login_required(login_url=login_url)
def family_detail(request, family_id):
    family = get_object_or_404(Family, pk=family_id)
    profile = get_display_profile(request).first()
    user_is_guest = profile.guest_user

    try:
        kids = Person.objects.filter(family_id=family_id).order_by(
            "birthyear", "sibling_seq", "id"
        )
    except Person.DoesNotExist:
        kids = None

    try:
        notes = Note.objects.filter(family_id=family_id)
    except Note.DoesNotExist:
        notes = None

    try:
        featured_images = Image.objects.filter(family_id=family_id).order_by(
            "id"
        ) & Image.objects.filter(featured=1)
    except Image.DoesNotExist:
        featured_images = None

    try:
        images = Image.objects.filter(family_id=family_id).order_by("year")
    except Image.DoesNotExist:
        images = None

    try:
        family_story_records = FamilyStory.objects.filter(family_id=family_id)
    except FamilyStory.DoesNotExist:
        family_story_records = None

    if family_story_records:
        stories = set()
        for record in family_story_records:
            this_story = Story.objects.get(id=record.story_id)
            stories.add(this_story)
    else:
        stories = None

    return render(
        request,
        "familytree/family_detail.html",
        {
            "family": family,
            "kids": kids,
            "notes": notes,
            "show_book": True,
            "featured_images": featured_images,
            "images": images,
            "user": profile.user,
            "stories": stories,
            "user_person": profile.person,
            "media_server": media_server,
            "user_is_guest": user_is_guest,
        },
    )


@login_required(login_url=login_url)
def image_detail(request, image_id):
    profile = get_display_profile(request).first()
    image = get_object_or_404(Image, pk=image_id)
    user_is_guest = profile.guest_user

    this_image_person, this_image_family, image_people = Image.image_subjects(image)
    image_full_path = media_server + "/image/upload/r_20/" + image.big_name

    return render(
        request,
        "familytree/image_detail.html",
        {
            "image": image,
            "image_person": this_image_person,
            "image_family": this_image_family,
            "show_book": False,
            "image_people": image_people,
            "user_person": profile.person,
            "image_full_path": image_full_path,
            "user": profile.user,
            "media_server": media_server,
            "user_is_guest": user_is_guest,
        },
    )


@login_required(login_url=login_url)
def image_index(request):
    template = "familytree/image_index.html"
    profile = get_display_profile(request).first()
    accessible_branches = get_valid_branches(request)
    user_is_guest = profile.guest_user

    image_cache_name = "images_" + str(profile.user)
    family_album_data = cache.get(image_cache_name)
    if not family_album_data:
        print("image_cache not there")
        family_album_data = get_image_index_data(accessible_branches, profile)
    else:
        print("did find image_cache")

    page = request.GET.get("page", 1)
    paginator = Paginator(family_album_data, 50)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = {
        "image_list": family_album_data,
        "accessible_branches": accessible_branches,
        "branch2_name": branch2_name,
        "profile": profile,
        "user_person": profile.person,
        "media_server": media_server,
        "user": profile.user,
        "items": items,
        "user_is_guest": user_is_guest,
    }
    return render(request, template, context)


# Save time on Family album page (aka image_index) by calling ahead for pictured_list.
# Elsewhere the template will retrieve it from cache
def get_image_index_data(accessible_branches, profile):
    image_list = Image.objects.none()
    for branch in accessible_branches:
        name = branch.display_name
        image_list = image_list.union(
            Image.objects.filter(branches__display_name__contains=name).order_by("year")
        )

    sorted_list = image_list.order_by("year")
    family_album_data = []
    for image in sorted_list:
        family_album_data.append([image, image.pictured_list])

    image_cache_name = "images_" + str(profile.user)
    cache.set(image_cache_name, family_album_data, 60 * 30)  # save this for 30 minutes
    print("image_cache is set")
    return family_album_data


#  receiver code to cache data as a user logs in
@receiver(post_save, sender=User)
def populate_album_and_outline_data(sender, instance, **kwargs):

    profile_queryset = Profile.objects.filter(user=instance)
    if (
        profile_queryset
    ):  # this is intended for user post_save of a login (not creation, where there isn't a profile yet)
        accessible_branches = Branch.objects.filter(profile__in=profile_queryset)
        get_image_index_data(accessible_branches, profile_queryset.first())
        get_outline_html(accessible_branches, profile_queryset.first())


# @TODO: Would prefer to do this in myauth/views form_valid while logging in, but different app can't import Profile
@receiver(post_save, sender=User)
def increment_profile_login_count(sender, instance, **kwargs):
    profile = Profile.objects.filter(user=instance).first()
    if profile:
        profile.login_count += 1
        profile.save()


@login_required(login_url=login_url)
def video_detail(request, video_id):
    show_mobile = request.user_agent.is_mobile or request.GET.get("show_mobile")
    profile = get_display_profile(request).first()
    video = get_object_or_404(Video, pk=video_id)
    video_people = Video.video_subjects(video)
    user_is_guest = profile.guest_user
    height = 200 if show_mobile else 400

    cloud_name = media_server.split("/")[3]
    public_id = video.name
    params = "cloud_name=" + cloud_name + "&public_id=" + public_id + "&vpv=1.4.0"
    video_url = "https://player.cloudinary.com/embed/?" + params

    return render(
        request,
        "familytree/video_detail.html",
        {
            "video": video,
            "video_people": video_people,
            "user": profile.user,
            "user_person": profile.person,
            "media_server": media_server,
            "video_url": video_url,
            "show_book": True,
            "user_is_guest": user_is_guest,
            "height": height,
        },
    )

@login_required(login_url=login_url)
def story_index(request):
    profile = get_display_profile(request).first()
    accessible_branches = get_valid_branches(request)
    existing_branches = Branch.objects.all()
    story_list = Story.objects.none()
    browser = request.user_agent.browser.family
    user_is_guest = profile.guest_user

    try:
        for branch in accessible_branches:
            this_branch_stories = (
                Story.objects.filter(
                    branches__display_name__contains=branch.display_name
                )
                .filter(dashboard_feature=True)
                .order_by("-id")
            )
            story_list = story_list | this_branch_stories
        combined_story_list = story_list.order_by("-id").distinct()[:30]
    except Story.DoesNotExist:
        combined_story_list = None


    if branch_count > 0:
        branch1_stories = set_branch_stories(existing_branches_list, 0)
    else:
        branch1_stories = None

    if branch_count > 1:
        branch2_stories = set_branch_stories(existing_branches_list, 1)
    else:
        branch2_stories = None

    if branch_count > 2:
        branch3_stories = set_branch_stories(existing_branches_list, 2)
    else:
        branch3_stories = None

    if branch_count > 3:
        branch4_stories = set_branch_stories(existing_branches_list, 3)
    else:
        branch4_stories = None


    context = {
        "story_list": combined_story_list,
        "accessible_branches": accessible_branches,
        "branch2_name": branch2_name,
        "user_person": profile.person,
        "branch1_stories": branch1_stories,
        "branch2_stories": branch2_stories,
        "branch3_stories": branch3_stories,
        "branch4_stories": branch4_stories,
        "branch1_name": branch1_name,
        "branch2_name": branch2_name,
        "branch3_name": branch3_name,
        "branch4_name": branch4_name,
        "browser": browser,
        "media_server": media_server,
        "user": profile.user,
        "user_is_guest": user_is_guest,
    }
    return render(request, "familytree/story_index.html", context)


@login_required(login_url=login_url)
def video_index(request):
    profile = get_display_profile(request).first()
    accessible_branches = get_valid_branches(request)
    existing_branches = Branch.objects.all()
    video_list = Video.objects.none()
    browser = request.user_agent.browser.family
    user_is_guest = profile.guest_user

    for branch in existing_branches:
        if branch in accessible_branches:
            name = branch.display_name
            video_list = video_list.union(
                Video.objects.filter(branches__display_name__contains=name).order_by(
                    "year"
                )
            )
    sorted_list = video_list.order_by("year")

    context = {
        "video_list": sorted_list,
        "accessible_branches": accessible_branches,
        "branch2_name": branch2_name,
        "user_person": profile.person,
        "media_server": media_server,
        "browser": browser,
        "user": profile.user,
        "user_is_guest": user_is_guest,
    }
    return render(request, "familytree/video_index.html", context)


@login_required(login_url=login_url)
def story(request, story_id):
    profile = get_display_profile(request).first()
    user_person = profile.person
    story = get_object_or_404(Story, pk=story_id)

    return render(
        request,
        "familytree/story.html",
        {"story": story, "media_server": media_server, "user_person": user_person, },
    )


@login_required(login_url=login_url)
def outline(request):
    profile = get_display_profile(request).first()
    accessible_branches = get_valid_branches(request)
    user_is_guest = profile.guest_user

    # Make a dictionary of original families by branch, for ex: [branch name]: [original families in that branch]
    users_original_families = {}
    for branch in accessible_branches:
        name = branch.display_name
        users_original_families[name] = Family.objects.filter(
            branches__display_name__contains=name, original_family=True
        )

    outline_cache_name = "outline_" + str(profile.user)
    outline_html = cache.get(outline_cache_name)
    if not outline_html:
        outline_html = get_outline_html(accessible_branches, profile)

    context = {
        "user_person": profile.person,
        "family_dict": users_original_families,
        "media_server": media_server,
        "show_book": True,
        "total_results_html": outline_html,
        "user": profile.user,
        "user_is_guest": user_is_guest,
    }

    return render(request, "familytree/outline.html", context)


def get_outline_html(accessible_branches, profile):
    total_results_html = {}
    user_is_guest = profile.guest_user

    # loop through the original families in each branch to make a dictionary of descendants
    for branch in accessible_branches:
        name = branch.display_name
        this_branch_results = []

        for family in Family.objects.filter(
            branches__display_name__contains=name, original_family=True
        ):
            this_family_results = get_descendants(family, user_is_guest)
            this_branch_results.append(this_family_results)

        this_branch_html = make_list_into_html(this_branch_results)
        total_results_html[name] = this_branch_html

    outline_cache_name = "outline_" + str(profile.user)
    cache.set(
        outline_cache_name, total_results_html, 60 * 30
    )  # save this for 30 minutes
    print("outline_cache is set")
    return total_results_html


def make_list_into_html(list):
    result = ""

    for item in list:
        if type(item) == Person:
            name = item.display_name
            path = root_url + "/people/" + str(item.id)
            link = '<li><a href="' + path + '">' + name + "</a></li>"
            result += link
        elif type(item) == Family:
            name = item.display_name
            path = root_url + "/families/" + str(item.id)
            link = '<ul><li><a href="' + path + '">' + name + "</a></li>"
            result += link
        else:
            html = make_list_into_html(item)
            result += html
            result += "</ul>"
    return result


def landing(request):
    show_mobile = request.user_agent.is_mobile or request.GET.get("show_mobile")
    landing_page_people = Person.objects.filter(
        living=False, show_on_landing_page=True
    ).order_by("last", "first")
    email_to = settings.ADMIN_EMAIL_ADDRESS

    template = (
        "familytree/landing_mobile.html" if show_mobile else "familytree/landing.html"
    )

    context = {
        "landing_page_people": landing_page_people,
        "media_server": media_server,
        "email_to": email_to,
    }
    return render(request, template, context)


@login_required(login_url=login_url)
def history(request):
    profile = get_display_profile(request).first()
    accessible_branches = get_valid_branches(request)
    user_is_guest = profile.guest_user

    context = {
        "accessible_branches": accessible_branches,
        "user_person": profile.person,
        "media_server": media_server,
        "profile": profile,
        "user": profile.user,
        "user_is_guest": user_is_guest,
    }
    return render(request, "familytree/history.html", context)


def logout(request):
    return render(request, "familytree/landing.html")


def get_valid_branches(request):
    profile = get_display_profile(request)
    accessible_branches = Branch.objects.filter(profile__in=profile)
    return accessible_branches


# typically we'll use the display for the logged-in-user, but superusers can view as other profiles
def get_display_profile(request):
    user = request.user
    profile = Profile.objects.filter(user=user)
    # if logged in as a superuser, also check for show_profile parameter
    if request.user.is_superuser:
        show_profile = request.GET.get("show_profile", None)
        if show_profile:
            profile = Profile.objects.filter(id=int(show_profile))
            print("viewing as profile: ", profile)
    return profile


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
                    if kid.sex == "F":
                        families_made = Family.objects.filter(wife=kid)
                    if kid.sex == "M":
                        families_made = Family.objects.filter(husband=kid)
                    if families_made:
                        for new_family in families_made:
                            next_results = get_descendants(
                                new_family, user_is_guest, these_results
                            )
                            these_results.extend([next_results])
    return these_results


@login_required(login_url=login_url)
def account(request):
    profile = get_display_profile(request).first()
    accessible_branches = get_valid_branches(request)
    notes_written = Note.objects.filter(author=profile.person.id)
    updates_made = (
        LogEntry.objects.filter(user_id=profile.user.id)
        .filter(Q(content_type_id=2) | Q(content_type_id=4))
        .filter(action_flag=2)
    )

    context = {
        "accessible_branches": accessible_branches,
        "user_person": profile.person,
        "user": profile.user,
        "media_server": media_server,
        "notes_written": notes_written,
        "updates_made": updates_made,
    }

    return render(request, "familytree/account.html", context)


@login_required(login_url=login_url)
def user_metrics(request):
    profile = get_display_profile(request).first()
    today = get_now_for_user(profile.timezone)
    month_ago_date = today.date() - relativedelta(days=30)

    accessible_branches = get_valid_branches(request)
    profiles = Profile.objects.all()
    existing_branches_list = list(Branch.objects.all())

    last_login_never = [x for x in profiles if not x.last_login()]
    last_login_past_month = [
        x for x in profiles if x.last_login() and x.last_login().date() > month_ago_date
    ]
    last_login_past_month.sort(reverse=True, key=lambda x: x.last_login())

    if branch_count > 0:
        branch1_users = Profile.objects.filter(
            branches__display_name__contains=existing_branches_list[0]
        )
    else:
        branch1_users = None
    if branch_count > 1:
        branch2_users = Profile.objects.filter(
            branches__display_name__contains=existing_branches_list[1]
        )
    else:
        branch2_users = None
    if branch_count > 2:
        branch3_users = Profile.objects.filter(
            branches__display_name__contains=existing_branches_list[2]
        )
    else:
        branch3_users = None
    if branch_count > 3:
        branch4_users = Profile.objects.filter(
            branches__display_name__contains=existing_branches_list[3]
        )
    else:
        branch4_users = None

    # Custom code for my instance, to differentiate between 3 generations of this website
    # A new instance would only need one count for logins, updates, and notes
    last_login_django_site = [
        x
        for x in profiles
        if x.last_login() and x.last_login().date() >= DJANGO_SITE_CREATION
    ]
    last_login_old_site_only = [
        x
        for x in profiles
        if x.last_login() and x.last_login().date() < LARAVEL_SITE_CREATION
    ]
    last_login_laravel_site = [
        x
        for x in profiles
        if x.last_login()
        and LARAVEL_SITE_CREATION < x.last_login().date() < DJANGO_SITE_CREATION
    ]

    profiles_who_made_notes_old = [x for x in profiles if x.notes_written("old")]
    profiles_who_made_notes_new = [x for x in profiles if x.notes_written("new")]

    profiles_who_made_edits_old = [x for x in profiles if x.edits_made("old")]
    profiles_who_made_edits_new = [x for x in profiles if x.edits_made("new")]

    context = {
        "accessible_branches": accessible_branches,
        "user_person": profile.person,
        "profiles": profiles,
        "last_login_never": last_login_never,
        "last_login_past_month": last_login_past_month,
        "branch1_users": branch1_users,
        "branch2_users": branch2_users,
        "branch3_users": branch3_users,
        "branch4_users": branch4_users,
        "existing_branches_list": existing_branches_list,
        "media_server": media_server,
        "user_timezone": profile.timezone,
        "profiles_who_made_edits_new": profiles_who_made_edits_new,
        "profiles_who_made_edits_old": profiles_who_made_edits_old,
        "last_login_laravel_site": last_login_laravel_site,
        "last_login_django_site": last_login_django_site,
        "last_login_old_site_only": last_login_old_site_only,
        "profiles_who_made_notes_old": profiles_who_made_notes_old,
        "profiles_who_made_notes_new": profiles_who_made_notes_new,
    }

    return render(request, "familytree/user_metrics.html", context)


def get_now_for_user(timezone_string):
    now = datetime.now().astimezone(timezone(timezone_string))
    return now
