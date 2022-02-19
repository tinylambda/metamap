from django.db import models
from django.utils.translation import gettext_lazy as _


def concept_hint_default():
    return {}


def attrib_datatype_default():
    return {
        'value_type': 'str',
        'collection_type': '',
        'key_type': '',
        'value_refer': '',  # refer to other attrib definition in another concept
        'gt': None,
        'ge': None,
        'lt': None,
        'le': None,
        'min_items': None,
        'max_items': None,
        'choices': None,
    }


def attrib_metadata_default():
    return {}


class Concept(models.Model):
    name = models.CharField(_('Concept name'), max_length=128)
    hint = models.JSONField(_('Concept hint'), blank=True, default=concept_hint_default)
    time_added = models.DateTimeField(_('Time Added'), auto_now_add=True)
    time_updated = models.DateTimeField(_('Time Updated'), auto_now=True)

    def __str__(self):
        return self.name


class Attrib(models.Model):
    of_concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    name = models.CharField(_('Attribute name'), max_length=64)
    datatype = models.JSONField(_('Attribute data type'), default=attrib_datatype_default)
    metadata = models.JSONField(_('Metadata'), blank=True, default=attrib_metadata_default)
    time_added = models.DateTimeField(_('Time Added'), auto_now_add=True)
    time_updated = models.DateTimeField(_('Time Updated'), auto_now=True)

    def __str__(self):
        return self.name
