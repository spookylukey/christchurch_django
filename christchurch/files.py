import re

from django.core.files.storage import FileSystemStorage
from django.utils.encoding import force_unicode


class FriendlyFileSystemStorage(FileSystemStorage):

    def get_valid_name(self, name):
        # Spaces are fine in names, underscores are ugly, so we override the
        # base implementation.
        return re.sub(r'(?u)[^-\w. ]', '', force_unicode(name).strip())

