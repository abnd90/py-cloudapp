# -*- coding: utf-8 -*-

#Copyright (C)2010 Abhinandh <abhinandh@gmail.com>
#This Program in licenser under General Public License Ver 3

import itertools, email, mimetypes, os

class MultiPartForm(object):

    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.formFields = []
        self.files = []
        self.boundary = b'AaB03x'

    def getContentType(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def addField(self, name, value):
        """Add a form field to the form data."""
        
        self.formFields.append((name, value))

    def addFile(self, filePath, fieldName='file'):
        """Add a file to be uploaded."""

        f = open(filePath, 'rb')
        body = f.read()
        fileName = os.path.basename(filePath)
        mimetype = mimetypes.guess_type(fileName)[0] or 'application/octet-stream'

        self.files.append((fieldName, fileName, mimetype, body))

    def toBytes(self):
        """Return a string representing the form data, including attached files."""

        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # refer http://www.ietf.org/rfc/rfc2388.txt (RFC2388)

        parts = []
        partBoundary = b'--' + self.boundary

        # Add the form fields

        parts.extend([ partBoundary,('Content-Disposition: form-data; name="%s"' % name).encode('utf-8'),
              b'', value.encode('utf-8'),] for name, value in self.formFields)

        # Add the files to upload
        # Amazon S3 expects file data to be 'Content-Disposition:
        # form-data' instead of "file"

        parts.extend([ partBoundary, ('Content-Disposition: form-data; name="%s"; filename="%s"' % \
              (fieldName, filename)).encode('utf-8'), ('Content-Type: %s' % contentType.encode('utf-8')).encode('utf-8'),b'',body,]
              for fieldName, filename, contentType, body in self.files)

        # Flatten the list and add closing boundary marker,
        # then return \r\n separated data

        flattened = list(itertools.chain(*parts))
        flattened.append(b'--' + self.boundary + b'--')
        flattened.append(b'')
        # print(flattened)
        return b'\r\n'.join(flattened) 
