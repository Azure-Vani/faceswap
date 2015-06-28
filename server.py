import os
import base64
import md5
import json
import os
import sys
sys.path.append('algo')

import Queue
import threading

import cherrypy
from cherrypy.process.plugins import SimplePlugin

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket

from faceswap import faceswap

class BackgroundTaskQueue(SimplePlugin):

    thread = None

    def __init__(self, bus, qsize=100, qwait=2, safe_stop=True):
        SimplePlugin.__init__(self, bus)
        self.q = Queue.Queue(qsize)
        self.qwait = qwait
        self.safe_stop = safe_stop

    def start(self):
        self.running = True
        if not self.thread:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def stop(self):
        if self.safe_stop:
            self.running = "draining"
        else:
            self.running = False

        if self.thread:
            self.thread.join()
            self.thread = None
        self.running = False

    def run(self):
        while self.running:
            try:
                try:
                    func, args, kwargs = self.q.get(block=True, timeout=self.qwait)
                except Queue.Empty:
                    if self.running == "draining":
                        return
                    continue
                else:
                    func(*args, **kwargs)
                    if hasattr(self.q, 'task_done'):
                        self.q.task_done()
            except:
                self.bus.log("Error in BackgroundTaskQueue %r." % self,
                             level=40, traceback=True)

    def put(self, func, *args, **kwargs):
        """Schedule the given func to be run."""
        self.q.put((func, args, kwargs))

class WebSocketHandler(WebSocket):
    def received_message(self, m):
        data = json.loads(m.data)
        print "[Websocket] Action: %s"%(data["action"])
        if data["action"] == "query":
            p = Process()
            try:
                p.run(self, data["content"])
            except:
                dict = {"action": "failed"}
                self.send(json.dumps(dict))
        else:
            print "[WebSocket] Unkonwn action"

class Process(object):
    def __init__(self):
        self.tmp_file_name = ""
        self.result_file_names = []

    def __del__(self):
        os.remove(self.tmp_file_name)
        for i in self.result_file_names:
            os.remove(i)

    def run(self, socket, data):
        print "[Run]"
        self.tmp_file_name = self.write_to_file(data)

        for step in faceswap(self.tmp_file_name):
            print "[Step] ", step
            if step["break"]: break
            if not step["finished"]:
                dict = {"action": "update", "status": step["status"]}
                socket.send(json.dumps(dict))
            else:
                name = step["name"]
                self.result_file_names.append(name)
                print "[Result]: "
                print "\t", name
                tmp = open(name, "r+b")
                dict = {"action": "finish", "data": self.fetch(tmp), "id": step["id"]}
                tmp.close()
                print "[WebSocket] Start transformission %d"%(step["id"])
                socket.send(json.dumps(dict))
                print "[WebSocket] End transformission %d"%(step["id"])

    def write_to_file(self, data):
        suffix, img_data = self.decode(data)
        print "[WebSocket] finished decoding image base64 data"
        hash = md5.md5(img_data).hexdigest()
        name = "%s.png"%(hash)
        file = open(name, "w+b")
        file.write(img_data)
        file.close()

        return name

    def fetch(self, file):
        raw_data = file.read()
        suffix = file.name.split(".")[-1]
        return self.encode(raw_data, suffix)

    def encode(self, raw_data, suffix):
        return "data:image/%s;base64,%s"%(suffix, base64.b64encode(raw_data))

    def decode(self, data):
        meta, raw_data = data.split(",")
        mime, encoding = meta.split(";")
        data_type, suffix = mime.split("/")
        return suffix, base64.b64decode(raw_data)

class Faceswap(object):

    @cherrypy.expose
    def index(self):
        return cherrypy.lib.static.serve_file(os.path.join(current_dir, "index.html"))

    @cherrypy.expose
    def ws(self):
        print "[WebSocket] Handler created: %s"%repr(cherrypy.request.ws_handler)

    @cherrypy.expose
    def echo(self): # This is a fake echo handler, actually
        return "Hello World\n"

    @cherrypy.expose
    def image(self):
        content_length = cherrypy.request.headers['Content-Length']
        raw_body = cherrypy.request.body.read(content_length)
        body = json.loads(raw_body)
        print "[Image Hanlder] Action: %s"%(data["action"])
        if data["action"] == "query":
            p = Process()
            try:
                p.run(self, data["content"])
            except:
                dict = {"action": "failed"}
                return json.dumps(dict)
        else:
            print "[Image Hanlder] Unkonwn action"

if __name__ == '__main__':
    url = '0.0.0.0'
    port = '80'
    if len(sys.argv) == 3:
        # then the URL has not been set
        url = sys.argv[1]
        port = sys.argv[2]

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # This 2 lines are basic routines for WebSocket and CherryPy
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.config.update({'server.socket_host': url,})
    cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', port)),})

    config = {
            "/static": {
                "tools.staticdir.on": True,
                "tools.staticdir.dir": os.path.join(current_dir, "static/")
                },
            "/ws": {
                "tools.websocket.on": True,
                "tools.websocket.handler_cls": WebSocketHandler
                }
            }

    cherrypy.config["tools.encode.on"] = False

    os.chdir('algo')
    cherrypy.quickstart(Faceswap(), "/", config)
