from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer


class IMultilingualToolsLayer(IDefaultPloneLayer):
    """Marker Interface used by BrowserLayer
    """


class IMultilingualForm(Interface):
    """ Marker interface for the linguatool form
    """

    def is_translatable():
        """ Helper method used for the linguatools object tab to see if it
            should render
        """


class IContentHelper(Interface):
    """ Methods for working on a content item.
        The implementation is different for Archetype and Dexterity context.
    """

    def get_translatable_fields():
        """ Returns all fields that are not language-independent """

    def check_for_title_attr(attrs):
        """ Makes sure the title attribute is present in the given list
            of attrs """

    def copy_attributes(trans, attrs):
        """ Copy the values of all given attributes from the source to the
            translation.
        """
