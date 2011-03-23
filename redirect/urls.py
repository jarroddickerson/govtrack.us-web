# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('redirect.views',
    url(r'^congress/person\.xpd$', 'person_redirect', name='person_redirect'),
    url(r'^congress/committee\.xpd$', 'committee_redirect', name='committee_redirect'),
    url(r'^congress/bill\.xpd$', 'bill_redirect', name='bill_redirect'),
)