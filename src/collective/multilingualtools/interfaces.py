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
