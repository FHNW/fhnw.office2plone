from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory

FHNWOffice2PloneMessageFactory = MessageFactory('fhnwoffice2plone')
ModuleSecurityInfo('fhnw.office2plone').declarePublic(
    'FHNWOffice2PloneMessageFactory')

def patch():
    from atreal.massloader import archives
    from .archives import OfficeArchive
    orig_available_archives = archives.available_archives
    archives.available_archives = orig_available_archives + [OfficeArchive,]
patch()
