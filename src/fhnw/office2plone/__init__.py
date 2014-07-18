from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory

FHNWSocialMediaMessageFactory = MessageFactory('fhnwoffice2plone')
ModuleSecurityInfo('fhnw.office2plone').declarePublic(
    'FHNWSocialMediaMessageFactory')
