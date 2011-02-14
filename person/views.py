# -*- coding: utf-8 -*-
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse

from common.decorators import render_to
from common.pagination import paginate

from person.models import Person

@render_to('person/person_details.html')
def person_details(request, pk):
    person = get_object_or_404(Person, pk=pk)
    if request.path != person.get_absolute_url():
        return redirect(person.get_absolute_url(), permanent=True)
    return {'person': person,
            }
