# -*- coding: utf-8 -*-
""" Base classes for package unit- and robot-testing
"""
__docformat__ = 'reStructuredText'
__author__ = 'Tom Gross <tom.gross@fhnw.ch>'


from plone.app.testing.bbb import PloneSandboxLayer, PloneTestCase
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.testing import z2
from plone.app import testing


class PackageFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import fhnw.office2plone
        self.loadZCML(package=fhnw.office2plone)
        z2.installProduct(app, 'fhnw.office2plone')

    def setUpPloneSite(self, portal):
        # install gs-profile to site
        testing.applyProfile(portal, 'fhnw.office2plone:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'fhnw.office2plone')


PTC_FIXTURE = PackageFixture()
PTC_FUNCTIONAL_TESTING = testing.FunctionalTesting(
    bases=(PTC_FIXTURE,), name='fhnw.office2plone:Functional')
PTC_ROBOT_TESTING = FunctionalTesting(
    bases=(PTC_FIXTURE, z2.ZSERVER_FIXTURE),
    name="fhnw.office2plone:Robot")


class TestCase(PloneTestCase):
    """ Base class used for test cases """

    layer = PTC_FUNCTIONAL_TESTING


class FunctionalTestCase(PloneTestCase):

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = z2.Browser(self.layer['app'])
        if loggedIn:
            browser.addHeader('Authorization', 'Basic %s:%s' %
                              (TEST_USER_NAME, TEST_USER_PASSWORD))
        return browser

# EOF
