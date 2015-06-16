from cadc.common.client import BaseClient
from cadc.data.transfer_reader import TransferReader
from cadc.data.transfer_writer import TransferWriter
from cadc.data.transfer import Transfer
import urlparse
import logging
import requests

class DataClient(BaseClient):
    """Class for interacting with the data web service"""


    def __init__(self, certfile=None, username=None, password=None,
                 schema_validate=False):
        """Data service client constructor."""

        super(DataClient, self).__init__(certfile=certfile, username=username,
                                           password=password)

        self.transfer_reader = TransferReader(validate=schema_validate)
        self.transfer_writer = TransferWriter()

        # Specific base_url for data webservice
        #self.base_url = self.base_url + '/data'
        #if self.is_authorized:
        #    self.base_url = self.base_url + '/auth'
        #else:
        #    self.base_url = self.base_url + '/pub'

        # hacked to test with VOSpace
        self.base_url = 'https://test.canfar.phys.uvic.ca'
        self.base_url = self.base_url + '/vospace/synctrans'

    def _make_logger(self):
        """ Logger for data client """
        self.logger = logging.getLogger('dataclient')

    def transfer_file(self, uri, localfile, is_put=False):
        """ Copy file to/from data/vos web service """

        # Direction-dependent setup
        if is_put:
            dir_str = 'to'
            tran = Transfer( uri,'pushToVoSpace' )
            f = open(localfile, 'rb')
        else:
            dir_str = 'from'
            tran = Transfer( uri,'pullFromVoSpace' )
            f = open(localfile, 'wb')

        self.logger.debug("Using service %s to transfer %s %s %s" %
                          (self.base_url, localfile, dir_str, uri) )

        # obtain list of endpoints by sending a transfer document and
        # looking at the URLs in the returned document
        request_xml = self.transfer_writer.write( tran )

        response = self._upload_xml( self.base_url, request_xml, 'POST' )

        quick_url = response.url
        response_str = response.text.encode('utf-8')

        self.logger.debug("POST had %i redirects" % len(response.history))
        self.logger.debug("Quick URL: %s" % quick_url)
        self.logger.debug("Full XML response:\n%s" % response_str)

        tran = self.transfer_reader.read( response_str )

        # Try transfering to/from endpoint until one works
        success = False
        for protocol in tran.protocols:
            url = protocol.endpoint
            self.logger.debug('Transfering %s %s...' % (dir_str, url) )

            try:
                if is_put:
                    r = requests.post(url, data=f)
                else:
                    r = requests.get(url, stream=True)
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
                self.logger.debug('Transfer %s %s %s failed:\n%s' %
                                  (url, localfile, dir_str, uri, str(e)) )
                continue
        f.close()

        if not success:
            raise Exception('Failed to download %s to %s' % (uri,localfile))

        # Do a HEAD to compare md5sums?
