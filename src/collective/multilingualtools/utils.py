import logging
import Acquisition

import zope.component

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.exceptions import ResourceLockedError
from Products.Archetypes.utils import shasattr
from Products.Archetypes.interfaces import IBaseContent, IBaseFolder
from Products.CMFPlone.utils import safe_unicode
from collective.multilingualtools.interfaces import IContentHelper
from collective.multilingualtools import HAS_DEXTERITY

from zope.component import adapts, getUtility, queryUtility, queryAdapter
from plone.behavior.interfaces import IBehavior
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY
from OFS.event import ObjectClonedEvent

from plone.app.portlets.utils import assignment_mapping_from_key
from plone.locking.interfaces import ILockable
from z3c.relationfield import RelationValue
from z3c.relationfield.interfaces import IRelationValue
from zope.app.intid.interfaces import IIntIds
from zope.event import notify
from zope.i18n import translate
from zope.i18n.interfaces import ITranslationDomain
from zope.interface import implements
from zope.i18nmessageid import Message
from zope.lifecycleevent import ObjectCopiedEvent
from Products.Five.utilities.interfaces import IMarkerInterfaces
from plone.multilingual.interfaces import (
    ILanguage,
    ITranslatable,
    ITranslationManager)

if HAS_DEXTERITY:
    from plone.dexterity.interfaces import IDexterityFTI
    from plone.dexterity.interfaces import IDexterityContent
    from plone.multilingualbehavior.interfaces import ILanguageIndependentField
    from plone.dexterity import utils as dexterityutils
else:
    class IDexterityContent(object):
        pass

log = logging.getLogger('collective.multilingualtools')
_marker = object()


class ATContentHelper(object):
    implements(IContentHelper)
    adapts(IBaseContent)

    def __init__(self, context):
        self.context = context

    def get_translatable_fields(self):
        field_info = []
        fields = [
            x for x in self.context.Schema().fields()
            if not x.languageIndependent]
        for field in fields:
            name = field.getName()
            if name not in ('id', 'language'):
                field_info.append((name, name))
        return field_info

    def check_for_title_attr(self, attrs):
        if "title" not in attrs:
            attrs.append("title")
        return attrs

    def copy_attributes(self, trans, attrs):
        res = []
        warnings = []
        for attr in attrs:
            field = self.context.getField(attr)
            if not field:
                warnings.append(
                    u"Could not find the field '%s'. Please "
                    "check your spelling" % attr)
                continue
            val = field.getAccessor(self.context)()
            trans.getField(attr).getMutator(trans)(val)
            res.append(u"  > Transferred attribute '%s'" % attr)
        # Set the correct format
        if shasattr(self.context, 'text_format'):
            trans.setFormat(self.context.text_format)
        if self.context.portal_type == 'Topic':
            # copy the contents as well
            ids = self.context.objectIds()
            ids.remove('syndication_information')

            # first delete all existing criteria on the translation
            for existingid in trans.objectIds():
                if existingid.startswith('crit__'):
                    trans._delObject(existingid)

            for id in ids:
                orig_ob = getattr(self.context, id)
                ob = orig_ob._getCopy(self.context)
                ob._setId(id)
                notify(ObjectCopiedEvent(ob, orig_ob))

                trans._setObject(id, ob)
                ob = trans._getOb(id)
                ob.wl_clearLocks()
                ob._postCopy(trans, op=0)
                ob.manage_afterClone(ob)
                notify(ObjectClonedEvent(ob))

            res.append(u"  > Transferred collection contents")
        return dict(res=res, warnings=warnings)


class DXContentHelper(object):
    implements(IContentHelper)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context
        self.language = ILanguage(self.context).get_language()
        self.fallbacks = [self.language.split('-')[0]]

    def get_translatable_fields(self):
        field_info = []
        fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        schemas = []
        schemas.append(fti.lookupSchema())
        for behavior_schema in dexterityutils.getAdditionalSchemata(
                self.context, self.context.portal_type):
            if behavior_schema is not None:
                schemas.append(behavior_schema)
        for schema in schemas:
            for field_name in schema:
                field = schema[field_name]
                if not ILanguageIndependentField.providedBy(field) \
                        and field_name != 'language':
                    title = field.title
                    # If the field's title is a translatable Message, get
                    # the correct translation for it. Use fallback in case
                    # we have a combined language code such as da-dk
                    if isinstance(title, Message):
                        trans_util = queryUtility(
                            ITranslationDomain, title.domain)
                        if trans_util:
                            trans_util.setLanguageFallbacks(self.fallbacks)
                            title = trans_util.translate(
                                title, self.language)
                        else:
                            title = translate(title, self.language)
                    # Mark required fields
                    if getattr(field, 'required', False):
                        title = "%s (*)" % title
                    field_info.append((
                        "%s|%s" % (field_name, schema.__identifier__),
                        title,
                    ))

        return field_info

    def check_for_title_attr(self, attrs):
        for attr in attrs:
            if attr.startswith('title|'):
                return attrs
        attrs.append('title|')
        return attrs

    def copy_attributes(self, trans, attrs):
        res = []
        warnings = []
        for attr in attrs:
            field_name, behavior_name = attr.split('|')
            behavior_interface = None
            behavior_instance = queryUtility(IBehavior, name=behavior_name)
            if behavior_instance is not None:
                behavior_interface = behavior_instance.interface
            if behavior_interface is not None:
                value = getattr(
                    behavior_interface(self.context), field_name, _marker)
            else:
                value = getattr(self.context, field_name, _marker)
            if IRelationValue.providedBy(value):
                obj = value.to_object
                adapter = queryAdapter(trans, ILanguage)
                if ITranslatable.providedBy(obj):
                    trans_obj = ITranslationManager(obj)\
                        .get_translation(adapter.get_language())
                    if trans_obj:
                        intids = getUtility(IIntIds)
                        value = RelationValue(intids.getId(trans_obj))
            if not (value == _marker):
                # We check if not (value == _marker) because
                # z3c.relationfield has an __eq__
                if behavior_interface is not None:
                    setattr(behavior_interface(trans), field_name, value)
                else:
                    setattr(trans, field_name, value)
                res.append(
                    u"  > Transferred attribute '%s'" % field_name)
        return dict(res=res, warnings=warnings)


def exec_for_all_langs(context, method, *args, **kw):
    """ helper method. Takes a method and executes it on all language
    versions of the context
    """
    info = []
    warnings = []
    errors = []
    changed_languages = []
    skipped_languages = []

    portal_url = getToolByName(context, 'portal_url')
    portal_path = portal_url.getPortalPath()

    manager = ITranslationManager(context)
    translations = manager.get_translations()
    content_language = ILanguage(context).get_language()
    langs = [x for x in translations.keys() if x != content_language]
    langs.append(content_language)
    kw['content_language'] = content_language

    context_path = context.getPhysicalPath()
    dynamic_path = portal_path + '/%s/' + \
        "/".join(context_path[len(portal_path) + 1:])
    if dynamic_path[-1] == "/":
        dynamic_path = dynamic_path[:-1]

    # if the special keyword 'target_id' is passed, try to retrieve an object
    # of that name from the current context and save it in the kw arguments.
    # This object can the used in the method for retrieving translations.
    # Needed when we are not working directly on translations of the current
    # context, but items contained in translations of the current context.
    if kw.get('target_id', None):
        target_object = getattr(context, kw.get('target_id'), None)
        if target_object:
            kw['target_object'] = target_object
    if kw.get('target_path', None):
        targetpath = safe_unicode(kw['target_path']).encode('utf-8')
        if targetpath.startswith('/'):
            if not targetpath.startswith(portal_path):
                targetpath = portal_path + targetpath
        target_base = context.restrictedTraverse(targetpath, None)
        kw['target_base'] = target_base

    # add the portal_path to the keywords
    kw['portal_path'] = portal_path

    for lang in langs:
        base = manager.get_translation(lang)
        if base is None:
            log.info("Break for lang %s, no translation present" % lang)
            skipped_languages.append(lang)
            continue

        kw['lang'] = lang
        err = method(base, *args, **kw)
        log.info("Executing for language %s" % lang)
        if err:
            errors.extend(err)
        else:
            changed_languages.append(lang)

    if changed_languages:
        info.append(
            'Executed for the following languages: %s'
            % ' '.join(changed_languages))

    if skipped_languages:
        warnings.append(
            'No translations for the following languages: %s'
            % ' '.join(skipped_languages))

    return info, warnings, errors


def block_portlets(ob, *args, **kw):
    """ Block the Portlets on a given context, manager, and Category """
    pl_managers = kw['managers']
    blockstatus = kw['blockstatus']
    for pl_managername, pl_manager in pl_managers.items():
        portletManager = zope.component.getUtility(
            IPortletManager, name=pl_managername)
        assignable = zope.component.getMultiAdapter(
            (ob, portletManager, ), ILocalPortletAssignmentManager)
        assignable.setBlacklistStatus(CONTEXT_CATEGORY, blockstatus)


def get_portlet_manager_names():
    names = [x[0] for x in zope.component.getUtilitiesFor(IPortletManager)]
    # filter out dashboard stuff
    names = [x for x in names if not x.startswith('plone.dashboard')]
    return names


def propagate_portlets(ob, *args, **kw):
    pl_managers = kw['managers']

    # skip current objects
    if kw['lang'] == kw['content_language']:
        return
    path = "/".join(ob.getPhysicalPath())

    for pl_managername, pl_manager in pl_managers.items():
        manager = assignment_mapping_from_key(
            ob, pl_managername, CONTEXT_CATEGORY, path)
        for x in list(manager.keys()):
            del manager[x]
        for x in list(pl_manager.keys()):
            manager[x] = pl_manager[x]


def renamer(ob, *args, **kw):
    """ rename one object within context from oldid to newid """
    err = list()
    oldid = kw['oldid']
    newid = kw['newid']
    if not oldid:
        err.append(u'Current id must not be empty')
    else:
        oldid = oldid.encode('utf-8')
    if not newid:
        err.append(u'New id must not be empty')
    else:
        newid = newid.encode('utf-8')
    if not err:
        if oldid not in ob.objectIds():
            manager = ITranslationManager(kw['target_object'])
            trans = manager.get_translation(kw['lang'])
            if trans:
                oldid = trans.getId()
        if oldid in ob.objectIds():
            ob.manage_renameObjects([oldid], [newid])
        else:
            err.append(
                'No translation for %s in language %s found in '
                'folder %s' % (oldid, kw['lang'],
                '/'.join(ob.getPhysicalPath())))
    return err


def set_po_title(ob, *args, **kw):
    """ simply set the title to a given value. Very primitive! """
    err = list()
    text = kw['text']
    lang = kw['lang']
    po_domain = kw['po_domain']
    if text == '':
        err.append(u"It is not allowed to set an empty title.")
    else:
        if po_domain != '':
            text = translate(
                target_language=lang, msgid=text, default=text,
                context=ob, domain=po_domain)
        ob.setTitle(text)
    return err


def set_po_description(ob, *args, **kw):
    """ simply set the title to a given value. Very primitive! """
    text = kw['text']
    po_domain = kw['po_domain']
    lang = kw['lang']
    if po_domain != '':
        text = translate(
            target_language=lang, msgid=text, default=text,
            context=ob, domain=po_domain)
    ob.setDescription(text)


def workflow_action(ob, *args, **kw):
    """ Changes the object's workflow state
    """
    err = list()
    transition = kw['transition']
    if not transition:
        err.append('Please select a workflow action.')
    if not err:
        portal_workflow = getToolByName(ob, 'portal_workflow')
        try:
            portal_workflow.doActionFor(ob, transition)
        except Exception, e:
            err.append(
                "Could not %(transition)s %(path)s. Error: %(error)s"
                % dict(transition=transition,
                path="/".join(ob.getPhysicalPath()),
                error=str(e)))
    return err


def set_property(ob, *args, **kw):
    err = list()
    id = kw['property_id']
    value = kw['property_value']
    type_ = kw['property_type']
    if not id:
        err.append('Property id must not be empty')
    if not value:
        err.append('Property value must not be emtpy')
    if not type_:
        err.append('Property type must not be emtpy')
    if not err:
        ob = Acquisition.aq_inner(ob)
        if Acquisition.aq_base(ob).hasProperty(id):
            try:
                ob._delProperty(id)
            except:
                err.append(
                    'Could not delete existing property %s on %s'
                    % (id, kw['lang']))
        try:
            ob._setProperty(id=id, value=value, type=type_)
        except:
            err.append(
                'Could not set property %s on %s'
                % (id, "/".join(ob.getPhysicalPath())))
    return err


def delete_property(ob, *args, **kw):
    err = list()
    id = kw['property_id']
    if not id:
        err.append('Property id must not be empty')
    if not err:
        ob = Acquisition.aq_inner(ob)
        if Acquisition.aq_base(ob).hasProperty(id):
            ob._delProperty(id)
        else:
            err.append(
                'The property %s does not exists on %s'
                % (id, "/".join(ob.getPhysicalPath())))
    return err


def cut_and_paste(ob, *args, **kw):
    """ Uses OFS to cut and paste an object.
    """
    err = list()
    if not kw['target_path']:
        err.append('You must specify a target path')
    id = kw['id_to_move']
    if not id:
        err.append(u'You must select an object to move')
    id = safe_unicode(id)
    if len(err):
        return err

    lang = kw['lang']
    target_base = kw['target_base']
    if target_base is None:
        err.append(
            u'No object was found at the given taget path %s'
            % kw['target_path'])
        return err
    if ITranslatable.providedBy(target_base):
        target_manager = ITranslationManager(target_base)
        target = target_manager.get_translation(lang)
    else:
        err.append(
            u'The target object is not translatable. Please '
            'choose a different target that is translatable.')
        return err
    if target is None:
        err.append(
            u'No translation in language "%s" was found of '
            'the target %s' % (lang, kw['target_path']))
        return err
    if not IBaseFolder.providedBy(target):
        err.append(
            u'The target object is not folderish - pasting is '
            'not possible.')
        return err
    name = None
    if id in ob.objectIds():
        name = id
        trans_object = getattr(ob, name)
    else:
        # look for translation via get_translation
        manager = ITranslationManager(kw['target_object'])
        trans_object = manager.get_translation(lang)
        if trans_object:
            if Acquisition.aq_parent(trans_object) == ob:
                name = trans_object.getId()

    if name is None:
        err.append(
            u'No translation of the requested object for language '
            '%s found in %s' % (lang, '/'.join(ob.getPhysicalPath())))
        return err
    if target == trans_object:
        err.append(
            u'The target cannot be identical to the object you want to move')
        return err

    # we need to pass a string
    name = safe_unicode(name).encode('utf-8')
    try:
        cut = ob.manage_cutObjects(name)
    except ResourceLockedError:
        lockable = ILockable(trans_object)
        lockable.unlock()
        cut = ob.manage_cutObjects(name)
    try:
        target.manage_pasteObjects(cut)
    except Exception, error:
        err.append(
            u'Not possible to paste item in language %s to target %s.'
            'Error message: %s' % (lang, target.absolute_url(), error))

    return err


def delete_this(ob, *args, **kw):
    err = list()
    lang = kw.get('lang', '')
    id_to_delete = kw['id_to_delete']
    name = ''

    if id_to_delete in ob.objectIds():
        name = id_to_delete
    else:
        # look for a translation of the item in the current language
        target_object = kw.get('target_object', None)
        if target_object:
            manager = ITranslationManager(target_object)
            trans_object = manager.get_translation(lang)
            if trans_object:
                name = trans_object.getId()

    if not name:
        err.append(u'No translation for language %s found' % lang)
    else:
        try:
            ob._delObject(name)
        except Exception, e:
            err.append(
                u'Could not delete %s for language %s. Message: %s'
                % (id_to_delete, lang, str(e)))
    return err


def translate_this(
        context, attrs=[], translation_exists=False, target_languages=[]):
    """ Translates the current object into all languages and transfers the
        given attributes
    """
    info = list()
    warnings = list()
    errors = list()

    # if context is language-neutral, it must receive a language before
    # it is translated
    lang_support = ILanguage(context)
    manager = ITranslationManager(context)
    if lang_support.get_language() == '':
        lang_support.set_language(
            context.portal_languages.getPreferredLanguage())
    canLang = lang_support.get_language()

    # if the user didn't select target languages, get all supported languages
    # from the language tool
    if not target_languages:
        portal_languages = getToolByName(context, 'portal_languages')
        target_languages = portal_languages.getSupportedLanguages()
    content_helper = IContentHelper(context)
    for lang in target_languages:
        if lang == canLang:
            continue
        res = list()
        if not manager.get_translation(lang):
            if not translation_exists:
                # need to make lang a string. It can be unicode so checkid will
                # freak out and lead to an infinite recursion
                manager.add_translation(str(lang))
                res.append("Added Translation for %s" % lang)
                # For a new translation, make sure the title is copied as well
                attrs = content_helper.check_for_title_attr(attrs)
            else:
                warnings.append(
                    u'Translation in language %s does not exist, '
                    'skipping' % lang)
                continue
        else:
            if not translation_exists:
                warnings.append(
                    u'Translation for language %s already '
                    'exists, skipping' % lang)
                continue
            res.append(u"Found translation for %s " % lang)
        trans = manager.get_translation(lang)
        content_results = content_helper.copy_attributes(trans, attrs)
        res.extend(content_results['res'])
        warnings.extend(content_results['warnings'])
        info.append(u"\n".join(res))
    return (info, warnings, errors)


def add_interface(ob, *args, **kw):
    """ Changes the object's workflow state
    """
    err = list()
    interface_to_add = kw['interface_to_add']
    if not interface_to_add:
        err.append('Please select an interface to add.')
    if not err:
        if type(interface_to_add) != list and type(interface_to_add) != tuple:
            interface_to_add = [interface_to_add]
        adapted = IMarkerInterfaces(ob)
        add = adapted.dottedToInterfaces(interface_to_add)
        adapted.update(add=add, remove=list())
    return err


def remove_interface(ob, *args, **kw):
    """ Changes the object's workflow state
    """
    err = list()
    interface_to_remove = kw['interface_to_remove']
    if not interface_to_remove:
        err.append('Please select an interface to remove.')
    if not err:
        if type(interface_to_remove) != list and \
                type(interface_to_remove) != tuple:
            interface_to_remove = [interface_to_remove]
        adapted = IMarkerInterfaces(ob)
        remove = adapted.dottedToInterfaces(interface_to_remove)
        adapted.update(add=list(), remove=remove)
    return err
