import doctest
import unittest

from plone.testing import layered

from qi.portlet.TagClouds.testing import TAGCLOUD_FUNCTIONAL_TESTING

optionflags = (doctest.NORMALIZE_WHITESPACE
               | doctest.ELLIPSIS
               | doctest.REPORT_NDIFF
               | doctest.REPORT_ONLY_FIRST_FAILURE)


normal_testfiles = ['edit_after_removal.txt']


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [layered(doctest.DocFileSuite(test,
                                      optionflags=optionflags),
                 layer=TAGCLOUD_FUNCTIONAL_TESTING)
         for test in normal_testfiles])
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
