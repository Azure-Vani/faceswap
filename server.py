import cherrypy
import os
import base64
import tempfile

class Faceswap(object):

    @cherrypy.expose
    def index(self):
        return cherrypy.lib.static.serve_file(os.path.join(current_dir, "index.html"))

    @cherrypy.expose
    def query(self, data):
        suffix, img_data = self.decode(data)
        file = tempfile.NamedTemporaryFile(suffix="."+suffix)
        print "[TempFile] Created file %s"%(file.name)
        file.write(img_data)
        return self.fetch(file)

    def fetch(self, file):
        raw_data = file.read()
        suffix = file.name.split(".")[-1]
        return self.encode(raw_data, suffix)

    def encode(self, raw_data, suffix):
        return "image/%s;base64,%s"%(suffix, base64.b64encode(raw_data))

    def decode(self, data):
        meta, raw_data = data.split(",")
        mime, encoding = meta.split(";")
        data_type, suffix = mime.split("/")
        return suffix, base64.b64decode(raw_data)

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))

    cherrypy.config.update({'server.socket_host': '0.0.0.0',})
    cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '80')),})

    config = {
            "/static": {
                "tools.staticdir.on": True,
                "tools.staticdir.dir": os.path.join(current_dir, "static/")
                }
            }
    cherrypy.quickstart(Faceswap(), "/", config)
