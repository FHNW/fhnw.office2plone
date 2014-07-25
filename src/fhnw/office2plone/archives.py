from atreal.massloader.archives import ZipArchive

class OfficeArchive(ZipArchive):

    mimetypes = ZipArchive.mimetypes + ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',]

    def listContent(self):
        all_contents = super(OfficeArchive, self).listContent()
        return [item for item in all_contents if item.startswith('word/media/')]
