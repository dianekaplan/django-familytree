from django.core.management.base import BaseCommand, CommandError
from ...models import Person, Family, Branch
from pathlib import Path

def get_descendants(family, results=None):
    these_results = [family]
    kids = None

    try:
        kids = Person.objects.filter(family=family).order_by('id')
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


def make_branch_list(branch):
    name = branch.display_name
    this_branch_results = []
    orig_family_list = Family.objects.filter(branches__display_name__contains=name, original_family=True)

    for family in orig_family_list:
        print("\n Add results for:" + family.display_name + ": ")
        this_family_results = get_descendants(family)
        # print(str(this_family_results))
        this_branch_results.append(this_family_results)
    results = this_branch_results
    print("\n Branch results: " + str(results))
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
            result += '</ul>'

    return result


class Command(BaseCommand):
    help = 'Generate outline view html for each branch'

    def handle(self, *args, **kwargs):
        path = Path("familytree/templates/familytree/outline_branch_partials")
        branches = Branch.objects.all()

        for branch in branches:
            name = branch.display_name
            results = make_branch_list(branch)
            html = make_list_into_html(results)

            filename = name + "_outline.html"
            path_plus_file = path.joinpath(filename)

            f = open(path_plus_file, 'w')
            f.write(str(html))
            f.closed
            print("Wrote file: " + filename)
