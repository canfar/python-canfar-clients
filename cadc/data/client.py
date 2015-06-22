from cadc.common.client import BaseClient
from cadc.data.transfer_reader import TransferReader
from cadc.data.transfer_writer import TransferWriter
from cadc.data.transfer import Transfer
from cadc.data.exceptions import TransferException
from cadc.common.exceptions import UnauthorizedException
import urlparse
import logging
import requests

class DataClient(BaseClient):
    """Class for interacting with the data web service"""

    def __init__(self, schema_validate=False, *args, **kwargs):
        """Data service client constructor."""

        super(DataClient, self).__init__(*args, **kwargs)

        self.transfer_reader = TransferReader(validate=schema_validate)
        self.transfer_writer = TransferWriter()

        # Specific base_url for data webservice
        self.base_url = self.base_url + '/data'
        if self.is_authorized:
            self.base_url = self.base_url + '/auth'
        else:
            self.base_url = self.base_url + '/pub'

    def _make_logger(self):
        """ Logger for data client """
        self.logger = logging.getLogger('dataclient')

    def transfer_file(self, uri, localfile, is_put=False, stream=None):
        """ Copy file to/from data/vos web service """

        # Direction-dependent setup
        if is_put:
            if not self.is_authorized:
                # We actually raise an exception here since the web
                # service will normally respond with a 200 for an
                # anonymous put, though not provide any endpoints.
                raise UnauthorizedException(
                    "Unauthorized clients cannot put files.")
            dir_str = 'to'
            tran = Transfer( uri, 'pushToVoSpace' )
            f = open(localfile, 'rb')
        else:
            dir_str = 'from'
            tran = Transfer( uri, 'pullFromVoSpace' )
            f = open(localfile, 'wb')

        # If a stream is supplied it goes in an Http header
        if stream is not None:
            headers = {'X-CADC-Stream':stream}
        else:
            headers = None

        self.logger.debug("Using service %s to transfer %s %s %s (%s)" %
                          (self.base_url, localfile, dir_str, uri,
                           str(stream)) )

        # obtain list of endpoints by sending a transfer document and
        # looking at the URLs in the returned document
        request_xml = self.transfer_writer.write( tran )
        response = self._upload_xml( self.base_url, request_xml, 'POST',
                                     headers=headers)
        response_str = response.text.encode('utf-8')

        self.logger.debug("POST had %i redirects" % len(response.history))
        self.logger.debug("Response code: %i, URL: %s" % \
                              (response.status_code,response.url) )
        self.logger.debug("Full XML response:\n%s" % response_str)

        tran = self.transfer_reader.read( response_str )

        # Try transfering to/from endpoint until one works
        success = False
        for protocol in tran.protocols:
            url = protocol.endpoint
            if url is None:
                self.logger.debug(
                    'No endpoint for URI, skipping.')
                continue

            self.logger.debug('Transfering %s %s...' % (dir_str, url) )

            try:
                if is_put:
                    r = requests.post(url, data=f)
                    self.check_exception(r)
                else:
                    r = requests.get(url, stream=True)
                    self.check_exception(r)
                    with open(localfile, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                f.flush

                success = True
                break
            except Exception as e:
                # Reset to start of file. Try next endpoint
                f.seek(0)
                self.logger.warning('Transfer %s %s %s failed:\n%s' %
                                    (str(localfile), str(dir_str), str(uri),
                                     str(e)) )
                continue
        f.close()

        if not success:
            msg = 'Failed to transfer %s %s %s. ' % (str(localfile),
                                                     str(dir_str), str(uri))
            msg = msg + 'File missing or user lacks permission?'
            self.logger.error(msg)
            raise TransferException(msg)

        # Do a HEAD to compare md5sums?

    def file_info(self, uri):
        """ Get information about a file at given uri """

        self.logger.info('Does not do anything yet')
