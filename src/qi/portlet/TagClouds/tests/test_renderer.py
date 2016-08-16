from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from qi.portlet.TagClouds import tagcloudportlet
from qi.portlet.TagClouds.testing import TAGCLOUD_FUNCTIONAL_TESTING
import unittest
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME


class TestRenderer(unittest.TestCase):

    layer = TAGCLOUD_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_test(self):
        self.assertTrue(True)

    def afterSetUp(self):
        """
        """
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        # Add a few documents tagged as "tag1" and publish them in
        # member's folder.
        portal.invokeFactory('Document', 'tag1_1')
        portal.tag1_1.editMetadata(subject='tag1')
        portal.portal_workflow.doActionFor(portal.tag1_1, 'publish')
        portal.invokeFactory('Document', 'tag1_2')
        portal.tag1_2.editMetadata(subject='tag1')
        portal.portal_workflow.doActionFor(portal.tag1_2, 'publish')
        portal.invokeFactory('Document', 'tag1_3')
        portal.tag1_3.editMetadata(subject='tag1')
        portal.portal_workflow.doActionFor(portal.tag1_3, 'publish')
        portal.invokeFactory('Document', 'tag1_4')
        portal.tag1_4.editMetadata(subject=['tag1', 'commontag'])
        portal.portal_workflow.doActionFor(portal.tag1_4, 'publish')

        # Add a few more with tag "tag2" and publish them too.
        portal.invokeFactory('Document', 'tag2_1')
        portal.tag2_1.editMetadata(subject='tag2')
        portal.portal_workflow.doActionFor(portal.tag2_1, 'publish')
        portal.invokeFactory('Document', 'tag2_2')
        portal.tag2_2.editMetadata(subject=['tag2', 'commontag'])
        portal.portal_workflow.doActionFor(portal.tag2_2, 'publish')

        # And yet another one in a subfolder
        portal.invokeFactory('Folder', 'subfolder')
        portal.portal_workflow.doActionFor(
            portal.subfolder, 'publish')
        portal.subfolder.invokeFactory('News Item', 'tag3_1')
        portal.subfolder.tag3_1.editMetadata(subject='tag3')
        portal.portal_workflow.doActionFor(
            portal.subfolder.tag3_1, 'publish')

        # Add a private object tagged as "privatetag" created by admin
        portal.invokeFactory('Document', 'private1')
        portal.private1.editMetadata(subject='adminprivate')

        # Add a private object tagged as "privatetag" created by a normal
        # #member
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Contributer'])
        login(portal, TEST_USER_NAME)
        self.folder.invokeFactory('Document', 'private2')
        self.folder.private2.editMetadata(subject='memberprivate')

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or context.REQUEST
        view = view or context.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=context)
        assignment = assignment or tagcloudportlet.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_levels(self):
        """Tests the 'levels' setting
        """
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        # Setup the portlet so that only one size is used.
        r = self.renderer(context=portal,
                          assignment=tagcloudportlet.Assignment(
                              levels=1,
                              wfStates=['published', 'private'],
                          ))
        r = r.__of__(portal)
        r.update()
        output = r.render()
        self.failUnless('cloud1' in output)
        self.failIf('cloud2' in output)

        # Setup the portlet so that there can be
        # up to 3 different tag sizes.
        r = self.renderer(context=portal,
                          assignment=tagcloudportlet.Assignment(
                              levels=3,
                              wfStates=['published', 'private'],
                          ))
        r = r.__of__(portal)
        r.update()
        output = r.render()
        self.failUnless('cloud1' in output)
        self.failUnless('cloud3' in output)

    def test_count(self):
        """Tests the 'count' setting.
        We choose to show the two most popular tags so only 'tag1' and 'tag2'
        should appear.
        """
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        r = self.renderer(context=portal,
                          assignment=tagcloudportlet.Assignment(
                              count=2,
                              wfStates=['published', 'private'],
                          ))
        r = r.__of__(portal)
        r.update()
        output = r.render()
        self.failUnless('tag1' in output)
        self.failUnless('tag2' in output)
        self.failIf('tag3' in output)

    def test_restrictSubjects(self):
        """Tests the restrictSubjects setting.
        We choose to show only items tagged by 'tag1' and 'tag3'.
        """
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        r = self.renderer(context=portal,
                          assignment=tagcloudportlet.Assignment(
                              restrictSubjects=['tag1', 'tag3'],
                              wfStates=['published', 'private'],
                          ))
        r = r.__of__(portal)
        r.update()
        output = r.render()
        self.failUnless('tag1' in output)
        self.failUnless('tag3' in output)
        self.failIf('tag2' in output)

    def test_filterSubjects(self):
        """Tests the filterSubjects setting
        We test by filtering by 'commontag' which should return
        only one item for 'tag1' and 'tag2'
        """
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        r = self.renderer(context=portal,
                          assignment=tagcloudportlet.Assignment(
                              filterSubjects=['commontag'],
                              wfStates=['published'],))
        r = r.__of__(portal)
        r.update()
        output = r.render()
        self.failUnless('tag1' in output)
        self.failUnless('tag2' in output)

    def test_restrictTypes(self):
        """Tests the restrictTypes setting.
        We choose to show only 'News item' content.
        """
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        r = self.renderer(context=portal,
                          assignment=tagcloudportlet.Assignment(
                              restrictTypes=['News Item'],
                              wfStates=['published', 'private'],
                          ))
        r = r.__of__(portal)
        r.update()
        output = r.render()
        self.failUnless('tag3' in output)
        self.failIf('tag1' in output)
        self.failIf('tag2' in output)
        self.logout()

    def test_root(self):
        """Tests setting the root of the search.
        """
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        r = self.renderer(context=portal,
                          assignment=tagcloudportlet.Assignment(
                              root='/subfolder',
                              wfStates=['published', 'private'],
                          ))
        r = r.__of__(portal)
        r.update()
        output = r.render()
        self.failUnless('tag3' in output)
        self.failIf('tag1' in output)
        self.failIf('tag2' in output)
        self.logout()

    def test_wfStates(self):
        """Tests the selection of which workflow states to display.
        Also checks whether view permissions are properly respected
        by the cache mechanism.
        """
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        r = self.renderer(context=portal,
                          assignment=tagcloudportlet.Assignment(
                              wfStates=['published'],
                          ))
        r = r.__of__(portal)
        r.update()
        output = r.render()
        self.failIf('adminprivate' in output)
        self.failIf('memberprivate' in output)

        r = self.renderer(context=portal,
                          assignment=tagcloudportlet.Assignment(
                              wfStates=['private'],
                          ))
        r = r.__of__(portal)
        r.update()
        output = r.render()
        self.failUnless('adminprivate' in output)
        self.failUnless('memberprivate' in output)

        #Login as a normal member. Should not be able to see private objects
        # from other users.
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Contributor'])
        login(portal, TEST_USER_NAME)
        r = self.renderer(context=portal,
                          assignment=tagcloudportlet.Assignment(
                              wfStates=['private'],
                          ))
        r = r.__of__(portal)
        r.update()
        output = r.render()
        self.failIf('adminprivate' in output)
        self.failUnless('memberprivate' in output)

    def test_searchLinks(self):
        """Make sure the parameters specified are also mirrored in the
        search links
        """
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        r = self.renderer(context=portal,
                          assignment=tagcloudportlet.Assignment(
                              wfStates=['private', 'published'],
                              restrictTypes=['News Item'],
                              root='/subfolder'))
        r = r.__of__(portal)
        r.update()
        output = r.render()
        self.failUnless("portal_type%3Alist=News%20Item" in output)
        self.failUnless("review_state%3Alist=private" in output)
        self.failUnless("review_state%3Alist=published" in output)
        self.failUnless("path=/plone/subfolder" in output)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRenderer))
    return suite
