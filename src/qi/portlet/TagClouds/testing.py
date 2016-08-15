from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.testing import z2
from Products.CMFCore.utils import getToolByName

from zope.configuration import xmlconfig


class TagCloudLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import qi.portlet.TagClouds
        xmlconfig.file('configure.zcml',
                       qi.portlet.TagClouds,
                       context=configurationContext)
        self.loadZCML(package=qi.portlet.TagClouds)
        z2.installProduct(app, 'qi.portlet.TagClouds')
        import plone.app.dexterity
        self.loadZCML(name='meta.zcml', package=plone.app.dexterity)
        self.loadZCML(package=plone.app.dexterity)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.dexterity:testing')
        self.applyProfile(portal, 'qi.portlet.TagClouds:default')
        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser(
            'contributor',
            'secret',
            ['Member', 'Contributor'],
            []
        )

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'qi.portlet.TagClouds')


TAGCLOUD_FIXTURE = TagCloudLayer()
TAGCLOUD_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(TAGCLOUD_FIXTURE, ),
                       name="qi.portlet.tagcloud:Integration")
TAGCLOUD_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(TAGCLOUD_FIXTURE, ),
                      name="qi.portlet.tagcloud:Functional")
