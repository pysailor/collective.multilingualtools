# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.Five.utilities.interfaces import IMarkerInterfaces
from collective.multilingualtools.interfaces import IContentHelper
from plone.multilingual.interfaces import (
    ILanguage,
    ITranslatable)
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtilitiesFor
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class PortletManagerVocabulary(object):
    """Vocabulary factory for portlet managers.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context
        # look up all portlet managers, but filter oit dashboard stuff
        names = [
            x[0] for x in getUtilitiesFor(IPortletManager)
            if not x[0].startswith('plone.dashboard')]
        terms = [SimpleTerm(x, title=x) for x in names]

        return SimpleVocabulary(terms)

PortletManagerVocabularyFactory = PortletManagerVocabulary()


class TranslatableFieldsVocabulary(object):
    """ Vocabulary factory for translatable fields on the current object"""

    implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context
        field_info = IContentHelper(context).get_translatable_fields()
        return SimpleVocabulary(
            [SimpleTerm(info[0], title=info[1]) for info in field_info])


TranslatableFieldsVocabularyFactory = TranslatableFieldsVocabulary()


class AvailableIdsVocabulary(object):
    """ Vocabulary that shows all ids in current folder """

    implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context
        # return all items in the current folder that are translatable
        terms = [
            SimpleTerm(id, title=u'%s (%s)' % (
                unicode(obj.Title(), 'utf-8'), id))
            for id, obj in context.objectItems()
            if ITranslatable.providedBy(obj)]

        return SimpleVocabulary(terms)

AvailableIdsVocabularyFactory = AvailableIdsVocabulary()


class PropertyTypesVocabulary(object):
    """ Vocabulary that returns all available types for OFS properties
        The list ist hard-coded, just like in the
        manage_propertiesForm of OFS...
    """
    TYPES_ = [
        'string', 'boolean', 'date', 'float', 'int', 'lines', 'long', 'text']
    implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context
        terms = [SimpleTerm(id, title=id) for id in self.TYPES_]

        return SimpleVocabulary(terms)

PropertyTypesVocabularyFactory = PropertyTypesVocabulary()


class AvailablePropertiesVocabulary(object):
    """ Vocabulary that returns all properties set on the current object
        The prop "title" is excluded
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context

        terms = [
            SimpleTerm(id, title="%s (%s)" % (id, title)) for
            id, title in context.propertyItems() if id != 'title']

        return SimpleVocabulary(terms)

AvailablePropertiesVocabularyFactory = AvailablePropertiesVocabulary()


class SupportedLanguagesVocabulary(object):
    """ Vocabulary that returns all supported languages of the site
        except for the current language
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context
        content_language = ILanguage(context).get_language()
        portal_languages = getToolByName(context, 'portal_languages')
        terms = [
            SimpleTerm(id, title=title) for id, title in
            portal_languages.listSupportedLanguages()
            if id != content_language]

        return SimpleVocabulary(terms)

SupportedLanguagesVocabularyFactory = SupportedLanguagesVocabulary()


class AvailableWorkflowTransitions(object):
    """ Vocabulary that returns all available workflow transition available on
        the current object.
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context
        terms = list()
        portal_workflow = getToolByName(context, 'portal_workflow')

        workflows = portal_workflow.getWorkflowsFor(context)
        for workflow in workflows:
            if getattr(workflow, 'transitions', None):
                terms.extend(
                    SimpleTerm(id, title=id) for id in workflow.transitions)

        return SimpleVocabulary(terms)

AvailableWorkflowTransitionsFactory = AvailableWorkflowTransitions()


class AvailableMarkerInterfaces(object):
    """ Vocabulary that returns all available marker interfaces for
        the current object.
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context
        adapted = IMarkerInterfaces(context)
        terms = [
            SimpleTerm(x, title=x) for x in
            adapted.getAvailableInterfaceNames()]
        return SimpleVocabulary(terms)

AvailableMarkerInterfacesFactory = AvailableMarkerInterfaces()


class ProvidedeMarkerInterfaces(object):
    """ Vocabulary that returns all directly provided marker interfaces for
        the current object.
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context
        adapted = IMarkerInterfaces(context)
        terms = [
            SimpleTerm(x, title=x) for x in
            adapted.getDirectlyProvidedNames()]
        return SimpleVocabulary(terms)

ProvidedeMarkerInterfacesFactory = ProvidedeMarkerInterfaces()
