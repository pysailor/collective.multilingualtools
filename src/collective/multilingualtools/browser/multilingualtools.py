import logging
from Acquisition import aq_inner
from zope.interface import implements
from plone.z3cform.layout import FormWrapper
from plone.z3cform import z2
import forms
from collective.multilingualtools.interfaces import IMultilingualForm
from plone.multilingual.interfaces import (
    ILanguage,
    ITranslatable,
    ITranslationManager)

log = logging.getLogger('collective.multilingualtools')


class MultilingualToolsView(FormWrapper):

    implements(IMultilingualForm)
    id = u'multilingualtools'

    form = None  # override this with a form class.
    forms = [
        forms.NamingForm,
        forms.PortletForm,
        forms.RenamingForm,
        forms.CutAndPasteForm,
        forms.DeleterForm,
        forms.ReindexForm,
        forms.WokflowForm,
        forms.PropertyForm,
        forms.MarkerInterfaceForm,
        forms.DuplicaterForm,
    ]

    def __init__(self, context, request):
        super(MultilingualToolsView, self).__init__(context, request)
        self.form_instances = \
            [form(aq_inner(self.context), self.request) for form in self.forms
                if form.display]
        self.form_instance = self.form_instances[0]

    def update(self):
        z2.switch_on(self, request_layer=self.request_layer)
        for form_instace in self.form_instances:
            form_instace.update()

    def contents(self):
        z2.switch_on(self, request_layer=self.request_layer)
        return ''.join([fi.render() for fi in self.form_instances])

    def render_form(self):
        """This method combines the individual forms and renders them.
        """
        return ''.join([fi() for fi in self.form_instances])

    def label(self):
        """ """
        return u"MultilingualTools - do ONE thing for ALL language versions"

    def is_translatable(self):
        """ Helper method used on the linguatools object tab to see if it
            should render
        """
        context = aq_inner(self.context)
        return ITranslatable.providedBy(context)

    def getContentLanguage(self):
        content_language = ILanguage(self.context).get_language()
        return content_language

    def getContentTranslations(self):
        manager = ITranslationManager(self.context)
        return manager.get_translations()
