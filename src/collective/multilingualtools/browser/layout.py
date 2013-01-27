import os
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
from collective.multilingualtools.browser.multilingualtools \
    import MultilingualToolsView


multilingualtools_layout = ZopeTwoFormTemplateFactory(
    os.path.join(os.path.dirname(__file__), 'templates/layout.pt'),
    form=MultilingualToolsView)
