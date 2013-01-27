from Products.CMFCore.utils import getToolByName

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from zope.configuration import xmlconfig


class MultilingualtoolsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    MANAGER_USER_NAME = 'manager'
    MANAGER_USER_PASSWORD = 'secret'

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.multilingualtools
        xmlconfig.file('configure.zcml',
                       collective.multilingualtools,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'collective.multilingualtools:default')

        # Creates some users
        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser(
            self.MANAGER_USER_NAME,
            self.MANAGER_USER_PASSWORD,
            ['Manager'],
            [],
        )

TEST_FIXTURE = MultilingualtoolsLayer()
MULTILINGUALTOOLS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TEST_FIXTURE,),
    name="CollectiveMultilingualtools:Integration")

