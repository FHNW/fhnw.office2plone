from Products.Five import BrowserView
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
import zipfile
import tempfile
import subprocess
from atreal.massloader.interfaces import IMassLoader
from lxml import etree
import hashlib
from cStringIO import StringIO

from transaction import commit

from collective.quickupload.portlet.quickuploadportlet import JAVASCRIPT

class ProcessError(Exception):
    """Raised if a spawned process terminated with exit code != 0.
    """


def run_process(cmd, stdin):
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    # wait for the process to terminate
    stdout, stderr = process.communicate(stdin)
    errcode = process.returncode

    if errcode != 0:
        raise ProcessError(stderr)

    return (stdout, stderr)


class DocxImporter(BrowserView):

    @property
    def massloader(self):
        return IMassLoader(self.context)


    def docx_import(self):
        form = self.request.form
        up_file = form['doc']
        filename = getattr(up_file, 'filename', '')

        # We need to save the data *before* extracting images
        # otherwise it is recognized as a ZIP not as office document
        data = up_file.read()

        # Extract images and create content out of it
        self._extract_images(up_file)
        commit()

        # Extract text to HTML
        self._extract_html(data, filename)

        if not form.get('ajax'):
        # XXX        IStatusMessage
            self.request.response.redirect(self.context.absolute_url())

    def _extract_images(self, up_file):
        status, log = self.massloader.process(up_file, False)

    def _extract_html(self, up_file, filename):
        cmd = 'java -jar /home/tom/bin/tika-app-1.5.jar -h -'
        html_result, stderr = run_process(cmd, up_file)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html_result), parser)
        html_body = tree.find('.//body')
        for img in html_body.findall('.//img'):
            src = img.attrib['src']
            if src.startswith("embedded:"):
                img_name = src[9:]
            img_obj = self.context.restrictedTraverse('word/media/' + img_name)
            img.attrib['src'] = 'resolveuid/' + img_obj.UID()

        id = self.massloader._safeNormalize(filename)

        ptypes = getToolByName(aq_inner(self.context), 'portal_types')
        ptypes.constructContent(type_name='Document',
                                 container=self.context, id=id, title=filename)
        doc = self.context[id]
        doc_body = etree.tostring(html_body).replace('body>', 'div>') # XXXXX
        doc.setText(doc_body)
        self.context.setDefaultPage(id)

    def javascript(self):
        return JAVASCRIPT
