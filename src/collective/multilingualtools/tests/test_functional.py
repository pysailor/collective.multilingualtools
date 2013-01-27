# -*- coding: utf-8 -*-
"""Functional Doctests for collective.multilingualtools

   These test are only triggered when Plone 4 (and plone.testing) is installed.
"""
import doctest

import unittest2 as unittest
import pprint

from plone.testing import layered

from collective.multilingualtools.testing import \
    MULTILINGUALTOOLS_INTEGRATION_TESTING


optionflags = (
    doctest.ELLIPSIS | \
    doctest.NORMALIZE_WHITESPACE | \
    doctest.REPORT_ONLY_FIRST_FAILURE)
testfiles = [
    'lttest.txt',
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(test,
                optionflags=optionflags,
                globs={'pprint': pprint.pprint},
            ),
            layer=MULTILINGUALTOOLS_INTEGRATION_TESTING)
        for test in testfiles])
    return suite



