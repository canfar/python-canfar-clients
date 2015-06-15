from cadc.common.client import BaseClient
from cadc.data.transfer_reader import TransferReader
from cadc.data.transfer_writer import TransferWriter
from cadc.data.transfer import Transfer
import urlparse
import logging
import requests

class DataClient(BaseClient):
    """Class for interacting with the data web service"""


    def __init__(self, certfile=None, username=None, password=None):
        """Data service client constructor."""

        super(DataClient, self).__init__(certfile=certfile, username=username,
                                           password=password)

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

    def get_file(self, uri, localfile):
        """ Get a file from data/vos web service """

        self.logger.debug("Service %s: Download %s to %s" %
                          (self.base_url,uri,localfile))

        # obtain list of endpoints by sending a transfer document and
        # looking at the URLs in the returned document
        request_xml = TransferWriter().write( Transfer(uri, 'pullFromVoSpace' ))
        response = self._upload_xml( self.base_url, request_xml, 'POST' )

        quick_url = response.url
        response_str = response.text.encode('utf-8')

        self.logger.debug("POST had %i redirects" % len(response.history))
        self.logger.debug("Quick URL: %s" % quick_url)
        self.logger.debug("Full XML response:\n%s" % response_str)

        tran = TransferReader().read( response_str )

        # Open localfile for writing
        f = open(localfile, 'wb')

        # Try downloading from endpoints until one works
        success = False
        for protocol in tran.protocols:
            url = protocol.endpoint

            try:
                self.logger.debug('Try downloading from %s to %s' % \
                                      (url,localfile))
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
                self.logger.debug('Download from %s failed:\n%s' % (url,
                                                                    str(e)) )
                continue
        f.close()

        if not success:
            raise Exception('Failed to download %s to %s' % (uri,localfile))

        # Do a HEAD to compare md5sums?

        def put_file(self, uri, localfile):
            """ Put a file to data/vos web service """

            # obtain list of endpoints by sending a transfer document and
            # looking at the URLs in the returned document
            request_xml = TransferWriter().write( Transfer(uri,
                                                           'pushToVoSpace' ))
            response = self._upload_xml( self.base_url, request_xml, 'POST' )
            tran = TransferReader().read( response.text )

            # Open localfile for reading
            f = open(localfile, 'rb')

            # Try uploading to endpoints until one works
            success = False
            for protocol in tran.protocols:
                url = protocol.endpoint

                try:
                    self.logger.debug('Try uploading %s to %s' % (localfile,
                                                                  url) )
                    r = requests.post(url, data=f)
                    success = True
                    break
                except:
                    # Reset to start of file. Try next endpoint
                    f.seek(0)
                    self.logger.debug('Upload to %s failed.' % url)
                    continue
            f.close()

            if not success:
                raise Exception('Failed to upload %s to %s' % (localfile,uri))

        # Do a HEAD to compare md5sums?
