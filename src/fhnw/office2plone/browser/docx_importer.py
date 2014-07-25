from Products.Five import BrowserView
import zipfile
import tempfile
import subprocess
from atreal.massloader.interfaces import IMassLoader
from lxml import etree


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

    def docx_import(self):
        up_file = self.request.form['doc']
        self._extract_images(up_file)
        self._extract_html(up_file)
        self.request.response.redirect(self.context.absolute_url())

    def _extract_images(self, up_file):
        status, log = IMassLoader(self.context).process(up_file, False)

    def _extract_html(self, up_file):
        cmd = 'java -jar /home/tom/bin/tika-app-1.5.jar -h -'
        stdout, stderr = run_process(cmd, up_file.read())
        print stderr, stdout
