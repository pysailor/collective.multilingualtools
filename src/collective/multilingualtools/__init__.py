from zope.i18nmessageid import MessageFactory
_ = MessageFactory('collective.multilungualtools')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    from AccessControl import allow_module
    allow_module('collective.mutlinugualtools')
