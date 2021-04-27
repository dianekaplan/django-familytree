from django.core.management.base import BaseCommand, CommandError
from ...models import Person, Family, Branch


def get_descendants(family, results=None):
    cumulative_results = results or []
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
    # if kids:
    #     # breakpoint()
    #     # cumulative_results.extend([these_results])
    #     # return cumulative_results
    #     return these_results
    # else:
    #     return these_results

    if kids:
        # breakpoint()
        # cumulative_results.extend([these_results])
        return these_results
    else:
        return these_results

    # if kids:
    #     return these_results
    # # else:
    # #     cumulative_results.extend([these_results])
    # #     return cumulative_results

def make_branch_list(branch):
    name = branch.display_name
    this_branch_results = []
    orig_family_list = Family.objects.filter(branches__display_name__contains=name, original_family=True)

    for family in orig_family_list:
        this_family_results = get_descendants(family)
        this_branch_results.append(this_family_results)

    results = this_branch_results[0]
    return results

def make_list_into_html(list):
    result = ''


    for item in list:
        if type(item) == Person:
            id = item.id
            name = item.display_name
            link = '<li><a href="{% url ' + "'person_detail' " + str(item.id) + ' %}">'+ name + "</a></li>"
            result += link
        elif type(item) == Family:
            id = item.id
            name = item.display_name
            link = '<ul><li><a href="{% url ' + "'family_detail' " + str(item.id) + ' %}">' + name + "</a></li>"
            result += link
        else:
            html = make_list_into_html(item)
            result += html

    return result

class Command(BaseCommand):
    help = 'Generate outline view html for each branch'

    person_skipped_count = 0;
    child_family_dict = {}  # map of gedcom child/family associations (eg. P7: F1)


    def handle(self, *args, **kwargs):

        branches = Branch.objects.all()

        for branch in branches:
            name = branch.display_name
            results = make_branch_list(branch)
            # print( name + " branch results: ")
            print(results)

            html = make_list_into_html(results)
            print(html)
            # print("HTML results:" + html)

            # filename = name + "_outline.html"
            # f = open(filename, 'w')
            # f.write(results)
            # f.closed