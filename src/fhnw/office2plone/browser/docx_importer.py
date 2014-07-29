import socket
import subprocess
from cStringIO import StringIO

from Products.Five import BrowserView
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from transaction import commit

from atreal.massloader.interfaces import IMassLoader
from collective.quickupload.portlet.quickuploadportlet import JAVASCRIPT
from lxml import etree

from fhnw.office2plone import FHNWOffice2PloneMessageFactory as _


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

class TikaConfig(object):

    host = 'localhost'
    port = 8077

def copy_stream(input_, output):
    """Reads from the ``input_`` stream or string and writes into
    the ``output``. It does this in a buffered fashion for making
    sure that we never hold the whole file in our memory.

    This is used for copying the file data from Plone into either
    a tempfile when tika is used locally or into the socket which
    connects to the tika server.
    """
    if isinstance(input_, basestring):
        output.write(input_)
        return

    while True:
        data = input_.read(1024)
        if not data:
            break
        output.write(data)


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
            IStatusMessage(self.request).addStatusMessage(_("Uploaded document."),
                                                          type="info")
            self.request.response.redirect(self.context.absolute_url())

    def _extract_images(self, up_file):
        status, log = self.massloader.process(up_file, False)

    def convert_server(self, document, filename=''):
        config = TikaConfig()   # TODO make this configurable some time (see ftw.tika)
        #log.info('Converting document with tika server: %s' % filename)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((config.host, config.port))
        input = sock.makefile()
        copy_stream(document, input)
        input.flush()
        sock.shutdown(socket.SHUT_WR)
        return input.read()

    def convert_local(self, document, filename=''):
        cmd = 'java -jar /home/tom/bin/tika-app-1.5.jar -h -'
        html_result, stderr = run_process(cmd, up_file)
        return html_result

    def _extract_html(self, up_file, filename):
        html_result = self.convert_server(up_file, filename)
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
        doc_body = etree.tostring(html_body).replace('body>', 'div>', 2) # XXXXX
        doc.setText(doc_body)
        self.context.setDefaultPage(id)

    def javascript(self):
        """ JavaScript needed for quickupload drag & drop """
        return JAVASCRIPT
