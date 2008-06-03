# -*- coding: utf-8 -*-
#
#   upload.py — Upload controller
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonnylamb@jonnylamb.com
#
#   Permission is hereby granted, free of charge, to any person
#   obtaining a copy of this software and associated documentation
#   files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use,
#   copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following
#   conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#   OTHER DEALINGS IN THE SOFTWARE.

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import os
import logging
import subprocess

from debexpo.lib.base import *
from debexpo.lib.utils import allowed_upload

log = logging.getLogger(__name__)

class UploadController(BaseController):

    def index(self, filename):
        log.info('File upload: %s' % filename)

        # Check the uploader's username and password
        self._check_credentials()

        # Check whether the file extension is supported by debexpo
        if not allowed_upload(filename):
            log.debug('File type not supported: %s' % filename)
            abort(403, 'The uploaded file type is not supported')

        if not config.has_key('debexpo.upload.incoming'):
            log.critical('debexpo.upload.incoming variable not set')
            abort(500, 'The incoming directory has not been set')

        if not os.path.isdir(config['debexpo.upload.incoming']):
            log.critical('debexpo.upload.incoming is not a directory')
            abort(500, 'The incoming directory has not been set up')

        if not os.access(config['debexpo.upload.incoming'], os.W_OK):
            log.critical('%s is not writable')
            abort(500, 'The incoming directory has not been set up')

        f = open(os.path.join(config['debexpo.upload.incoming'], filename), 'wb')

        while True:
            # Write to file in chunks of 10 KiB
            chunk = request.body.read(10240)
            if not chunk:
                # The upload is complete
                f.close()
                break
            else:
                f.write(chunk)

        # The .changes file is always sent last, so after it is sent,
        # call the importer process.
        if filename.endswith('.changes'):
            command = '%s -i %s -c %s' % (config['debexpo.importer'],
                config['global_conf']['__file__'], filename)

            subprocess.Popen(command, shell=True, close_fds=True)

    def _check_credentials(self):
        pass
