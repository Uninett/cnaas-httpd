from flask import request
from flask_restful import Resource
from cnaas_httpd.api.generic import empty_result

import urllib
from hashlib import sha1


class FirmwareFetchApi(Resource):
    def error(self, errstr):
        return empty_result(status='error', data=errstr), 404

    def url_parse(self, url):
        parsed = urllib.parse.urlparse(url)
        return parsed.path.split('/')[-1]

    def file_sha1(self, fname):
        hash_sha1 = sha1()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha1.update(chunk)
        return hash_sha1.hexdigest()

    def file_download(self, url, checksum, filename):
        path = '/opt/cnaas/www/firmware/' + filename
        try:
            urllib.request.urlretrieve(url, filename=path)
        except Exception as e:
            return e
        file_sha1 = self.file_sha1(path)
        if file_sha1 != checksum:
            return 'Checksum mismatch, file corrupt'
        return ''

    def post(self):
        json_data = request.get_json()

        if 'url' not in json_data:
            return self.error('URL must be specified')
        if 'sha1' not in json_data:
            return self.error('Checksum must be specified')

        filename = self.url_parse(json_data['url'])
        if filename == '':
            return self.error('Invalid URL, could not parse filename')
        res = self.file_download(json_data['url'], json_data['sha1'],
                                 filename)
        if res != '':
            return self.error(res)
        return empty_result(status='success')
