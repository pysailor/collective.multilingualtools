from collective.multilingualtools import _
from zope import interface, schema
from z3c.form import button


class INamingSchema(interface.Interface):
    """ Base Schema for the edit form. It is dynamically extended by plugins
    """
    text = schema.Text(
        title=_("title_text", default=u"Text"),
        description=_(
            "description_text", default=u"Type some text. This text will then "
            u"be written on all translations as Title or Description, "
            u"depending on which of the two buttons you click."),
        required=True,
    )

    po_domain = schema.TextLine(
        title=_("title_po_domain", default=u"PO Domain"),
        description=_(
            "description_po_domain", default=u"Give a po domain here, if you "
            u"have typed a message id in the field above. The translation in "
            u"this po-domain of the text you have typed will then be written "
            u"as Title / Description. If you leave the domain empty or state a"
            u"non-existing one, the text above will be written verbatim."),
        default=u"plone",
        required=False,
    )

    set_title = button.Button(title=u'Set text as Title')
    set_description = button.Button(title=u'Set text as Description')


class IObjectHandlingSchema(interface.Interface):
    """ object handling """

    old_id = schema.Choice(
        title=_("title_old_id", default=u"Object to rename"),
        description=_(
            "description_old_id", default=u"Choose an object to rename. The "
            u"drop-down displays the available objects with their titles plus "
            u"their id in bracktets."),
        required=False,
        vocabulary="multilingualtools.vocabularies.available_ids",
    )

    new_id = schema.TextLine(
        title=_("title_new_id", default=u"New id"),
        description=_(
            "description_new_id", default=u"Enter the id (short name) that"
            u"all translations of this item should receive."
        ),
        required=False,
    )

    id_to_delete = schema.Choice(
        title=_("title_id_to_delete", default=u"Object to delete"),
        description=_(
            "description_id_to_delete", default=u"Select an object that should"
            u" be deleted in all languages."),
        required=False,
        vocabulary="multilingualtools.vocabularies.available_ids",
    )

    id_to_move = schema.Choice(
        title=_("title_id_to_move", default=u"Object to move"),
        description=_(
            "description_id_to_move", default=u"Choose an object to move."),
        required=False,
        vocabulary="multilingualtools.vocabularies.available_ids",
    )

    target_path = schema.TextLine(
        title=_("title_target_path", default=u"Target path"),
        description=_(
            "description_target_path", default=u"Enter either an absolute path"
            u" or a path relative to the current location. Examples: "
            u"'/en/path/to/folder' (absolute); 'subfolder/from/here' or '../'"
            u" (relative)"),
        required=False,
    )

    rename = button.Button(title=u'Rename')
    delete = button.Button(title=u'Delete')
    cut_and_paste = button.Button(title=u'Cut and paste')


class IPortletSchema(interface.Interface):
    """ Portlet Schema for the edit form. """
    propagate_portlets = button.Button(title=u'Propagate Portlets')

    block_portlets = button.Button(title=u'Block Portlets')

    blockstatus = schema.Bool(
        title=_("title_blockstatus", default=u"Check to block"),
        description=u"",
        required=False,
    )

    portlet_manager = schema.Choice(
        title=_("title_portlet_manager", default=u"Portlet manager"),
        description=_(
            "description_portlet_manager", default=u"Select a portlet manager"
            u" on which to perform the desired action. Leave unselected to "
            u"perform the action for all portlet slots."),
        required=False,
        vocabulary="multilingualtools.vocabularies.portletmanagers",
    )


class IReindexSchema(interface.Interface):
    """ Schema for the Reindex All form. """
    reindex_all = button.Button(title=u'Reindex all')


class IWorkflowSchema(interface.Interface):
    """ Schema for the Publish All form. """
    do_action = button.Button(title=u'Perform workflow change')

    transition = schema.Choice(
        title=_("title_transition", default=u"Available actions"),
        description=_(
            "description_transition", default=u"Use this form to change the "
            u"workflow status of the current object and all translations."),
        required=False,
        vocabulary="multilingualtools.vocabularies.available_wf_transitions",
    )


class IDuplicaterSchema(interface.Interface):
    """ Schema for object duplication"""
    translate_this = button.Button(title=u'Translate this object')

    attributes_to_copy = schema.List(
        title=_("title_attributes_to_copy", default=u'Attributes to copy'),
        description=_(
            "description_attributes_to_copy", default=u"Select one or more "
            u"attributes to have their values copied over to the "
            u"translations. Attributes that are required on this content type "
            u"are marked with an asterisk, but you don't need to select them."),
        default=list(),
        required=False,
        value_type=schema.Choice(
            vocabulary="multilingualtools.vocabularies.translatable_fields",
        ),
    )

    target_languages = schema.List(
        title=_(
            "title_target_languages", default=u'Manual language selection'),
        description=_(
            "description_target_languages", u'Select the languages to which '
            u'you want to make a copy of the current object. Leave blank to '
            u'use all available languages.'),
        default=list(),
        required=False,
        value_type=schema.Choice(
            vocabulary="multilingualtools.vocabularies.supported_languages",
        ),
    )

    use_parent_languages = schema.Bool(
        title=_(
            "title_use_parent_languages", default=u"Use parent folder's "
            u"languages"),
        description=_(
            "description_use_parent_languages", default=u'Tick this box to '
            u'copy the object to all languages in which the folder that '
            u'contains it (= parent folder) is available. This setting takes '
            u'precedence over the manual selection above.'),
        required=False,
    )

    translation_exists = schema.Bool(
        title=_("title_translation_exists", default=u"Translation exists"),
        description=_(
            "description_translation_exists", default=u"Tick this box if a "
            u"translation already exits and you just want to propagate "
            u"attributes or Collection criteria"),
        required=False,
    )


class IPropertySchema(interface.Interface):
    """ Schema for setting and removing properties """

    property_id = schema.TextLine(
        title=_("title_property_id", default=u"Property id"),
        description=_(
            "description_property_id", default=u"Enter a property id"),
        required=False,
    )

    property_type = schema.Choice(
        title=_("title_property_type", default=u"Property type"),
        description=_(
            "description_property_type", default=u"Select the correct property"
            u" type"),
        required=False,
        default='string',
        vocabulary="multilingualtools.vocabularies.available_property_types",
    )

    property_value = schema.TextLine(
        title=_("title_property_value", default=u"Property value"),
        description=_(
            "description_property_value", default=u"Enter a value for the "
            u"property"),
        required=False,
    )

    property_to_delete = schema.Choice(
        title=_("title_property_to_delete", default=u"Property to delete"),
        description=_(
            "description_property_to_delete", default=u"Select a property to "
            u"delete"),
        required=False,
        vocabulary="multilingualtools.vocabularies.available_property_ids",
    )

    set_property = button.Button(title=u'Set property')
    delete_property = button.Button(title=u'Delete property')


class IMarkerInterfacesSchema(interface.Interface):
    """ Schema for the marker interface form. """
    remove_interface = button.Button(title=u'Remove selected interface')
    add_interface = button.Button(title=u'Add selected interface')

    interface_to_add = schema.Choice(
        title=_("title_interface_to_add", default=u"Available interfaces"),
        description=_(
            "description_interface_to_add", default=u"Select a marker "
            u"interface to be added to all translations"),
        required=False,
        vocabulary="multilingualtools.vocabularies.available_interfaces",
    )

    interface_to_remove = schema.Choice(
        title=_("title_interface_to_remove", default=u"Provided interfaces"),
        description=_(
            "description_interface_to_remove", default=u"Select a marker "
            u"interface to be removed from all translations."),
        required=False,
        vocabulary="multilingualtools.vocabularies.provided_interfaces",
    )
