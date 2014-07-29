# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_inner
from ZODB.POSException import ConflictError
from collective.quickupload import logger
from collective.quickupload.interfaces import IQuickUploadCapable
from thread import allocate_lock
from zope import component

import transaction

from zope.container.interfaces import INameChooser


upload_lock = allocate_lock()


from collective.quickupload.browser.uploadcapable import get_id_from_filename
from collective.quickupload.browser.uploadcapable import QuickUploadCapableFileFactory


class IQuickUploadOfficeCapable(IQuickUploadCapable):
    """ """

from StringIO import StringIO

class FileObj(StringIO):

    _filename = ''

    def _getFilename(self):
        return self._filename

    def _setFilename(self, filename):
        self._filename = filename

    filename = property(_getFilename, _setFilename)


class QuickUploadOfficeCapableFileFactory(QuickUploadCapableFileFactory):
    component.adapts(IQuickUploadOfficeCapable)

    def __call__(self, filename, title, description, content_type, data,
                 portal_type):
        context = aq_inner(self.context)
        error = ''
        result = {}
        result['success'] = None
        newid = get_id_from_filename(filename, context)
        chooser = INameChooser(context)
        newid = chooser.chooseName(newid, context)
        # consolidation because it's different upon Plone versions
        if not title:
            # try to split filenames because we don't want
            # big titles without spaces
            title = filename.rsplit('.', 1)[0]\
                .replace('_', ' ')\
                .replace('-', ' ')

        if newid in context:
            # only here for flashupload method since a check_id is done
            # in standard uploader - see also XXX in quick_upload.py
            raise NameError, 'Object id %s already exists' % newid
        else:
            upload_lock.acquire()
            try:
                transaction.begin()
                try:
                    from zope.publisher.browser import TestRequest
                    request = TestRequest()
                    dataobj = FileObj(data)
                    dataobj.filename = filename
                    request.form['doc'] = dataobj
                    request.form['ajax'] = '1'
                    from fhnw.office2plone.browser.docx_importer import DocxImporter
                    docximport = DocxImporter(self.context, request)
                    docximport.docx_import()
                except ImportError:
                    error = ''
                except Unauthorized:
                    error = u'serverErrorNoPermission'
                except ConflictError:
                    # rare with xhr upload / happens sometimes with flashupload
                    error = u'serverErrorZODBConflict'
                except ValueError:
                    error = u'serverErrorDisallowedType'
                except Exception, e:
                    error = u'serverError'
                    logger.exception(e)

                if error:
                    if error == u'serverError':
                        logger.info(
                            "An error happens with setId from filename, "
                            "the file has been created with a bad id, "
                            "can't find %s", newid)
                else:
                    pass

                #@TODO : rollback if there has been an error
                transaction.commit()
            finally:
                upload_lock.release()

        result['error'] = error
        if not error:
            result['success'] = self.context

        return result
