# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse

from common import enum

class CommitteeType(enum.Enum):
    senate = enum.Item(1, 'Senat')
    joint = enum.Item(2, 'Joint')
    house = enum.Item(3, 'House')


class Committee(models.Model):
    """
    Holds info about committees and subcommittees.

    Subcommittees have only code, name, parent nonblank attributes.
    """

    # committee_type makes sense only for committees
    committee_type = models.IntegerField(choices=CommitteeType, blank=True, null=True)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    abbrev = models.CharField(max_length=255, blank=True)
    obsolete = models.BooleanField(blank=True, default=False)
    committee = models.ForeignKey('self', blank=True, null=True, related_name='subcommittees')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        parent = self.committee
        if parent:
            return reverse('subcommittee_details', args=[parent.code, self.code])
        else:
            return reverse('committee_details', args=[self.code])
    
    def fullname(self):
        if self.committee == None:
            return self.name
        else:
            return self.committee.name + " Subcommittee on " + self.name
    
    def create_events(self):
        from events.feeds import AllCommitteesFeed, CommitteeFeed
        from events.models import Event
        with Event.update(self) as E:
            for meeting in self.meetings.all():
                E.add("mtg_" + str(meeting.id), meeting.when, AllCommitteesFeed())
                E.add("mtg_" + str(meeting.id), meeting.when, CommitteeFeed(self.code))
                # TODO bills
	
    def render_event(self, eventid, feeds):
        eventinfo = eventid.split("_")
        mtg = CommitteeMeeting.objects.get(id=eventinfo[1])
        
        import events.feeds
        return {
            "type": "Committee Meeting",
            "date": mtg.when,
            "title": self.fullname() + " Meeting",
			"url": self.get_absolute_url(),
            "body_text_template": """{{subject|safe}}""",
            "body_html_template": """{{subject}}""",
            "context": {
                "subject": mtg.subject,
                }
            }


class CommitteeMemberRole(enum.Enum):
    exofficio = enum.Item(1, 'Ex Officio')
    chairman = enum.Item(2, 'Chairman')
    ranking_member = enum.Item(3, 'Ranking Member')
    vice_chairman = enum.Item(4, 'Vice Chairman')
    member = enum.Item(5, 'Member')

class CommitteeMember(models.Model):
    person = models.ForeignKey('person.Person', related_name='assignments')
    committee = models.ForeignKey('committee.Committee', related_name='members')
    role = models.IntegerField(choices=CommitteeMemberRole, default=CommitteeMemberRole.member)

    def __unicode__(self):
        return '%s @ %s as %s' % (self.person, self.committee, self.get_role_display())

MEMBER_ROLE_WEIGHTS = {
    CommitteeMemberRole.chairman: 5,
    CommitteeMemberRole.vice_chairman: 4,
    CommitteeMemberRole.ranking_member: 3,
    CommitteeMemberRole.exofficio: 2,
    CommitteeMemberRole.member: 1
}

class CommitteeMeeting(models.Model):
    """Meetings that are scheduled in the future. Since we can't track meeting time changes,
    we have to clear these out each time we load up new meetings."""
    committee = models.ForeignKey('committee.Committee', related_name='meetings')
    when = models.DateTimeField()
    subject = models.TextField()
    # TODO: bills
