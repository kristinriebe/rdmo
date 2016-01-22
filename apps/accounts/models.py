from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Permission
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField


@python_2_unicode_compatible
class Profile(models.Model):
    user = models.OneToOneField(User)
    details = JSONField(null=True, blank=True)

    @property
    def full_name(self):
        if self.user.first_name and self.user.last_name:
            return '%s %s' % (self.user.first_name, self.user.last_name)
        else:
            return self.user.username

    def as_dict(self):
        detail_keys = DetailKey.objects.all()
        return {detail_key: self.details[detail_key.key] for detail_key in detail_keys}

    def as_dl(self):
        html = '<dl>'
        html += '<dt>%s</dt><dd>%s</dd>' % ('Name', self.full_name)
        for detail_key in DetailKey.objects.all():
            if self.details and detail_key.key in self.details:
                html += '<dt>%s</dt><dd>%s</dd>' % (detail_key.key.upper(), self.details[detail_key.key])
        html += '</dl>'
        return html

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ('user',)

        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')


@python_2_unicode_compatible
class DetailKey(models.Model):

    TYPE_CHOICES = (
        ('text', 'Text'),
        ('textarea', 'Textarea'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio button'),
        ('select', 'Select'),
        ('multiselect', 'Multiselect'),
    )

    key = models.SlugField()
    label = models.CharField(max_length=256)
    type = models.CharField(max_length=11, choices=TYPE_CHOICES)
    help_text = models.TextField(blank=True, help_text=_('Enter a help text to be displayed next to the input element'))
    options = JSONField(null=True, blank=True, help_text=_('Enter valid JSON of the form [[key, label], [key, label], ...]'))
    required = models.BooleanField()

    def __str__(self):
        return self.key

    class Meta:
        ordering = ('key',)

        verbose_name = _('DetailKey')
        verbose_name_plural = _('DetailKeys')


def create_profile_for_user(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        profile = Profile()
        profile.user = user
        profile.save()

post_save.connect(create_profile_for_user, sender=User)