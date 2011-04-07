import optparse
import simplejson

import bottle
import tornado.web
import tornado.ioloop

class ResponseGenerator(object):

    def __init__(self, filepath):
        self.entries = []
        self.position = 0
        with open(filepath) as f:
            for line in f:
                self.entries.append(simplejson.loads(line))

    def get_object(self):
        obj = self.entries[self.position]
        self.position += 1
        if self.position == len(self.entries):
            self.position = 0
        return obj

response_generator = None

class JSONHandler(tornado.web.RequestHandler):

    def get(self):
        self.set_header('Content-Type', 'application/json')
        self.write(simplejson.dumps(response_generator.get_object()))

@bottle.route('/')
def bottle_handler():
    return simplejson.dumps(response_generator.get_object())

if __name__ == '__main__':
    global response_generator
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', help='file of lines to input')
    opts, args = parser.parse_args()
    if len(args) != 1:
        parser.error('usage: server.py [bottle|tornado]')

    mode = args[0]
    if mode not in ('tornado', 'bottle', 'bottle-paste', 'bottle-cherry'):
        parser.error('usage: server.py [bottle|bottle-cherry|bottle-paste|tornado]')

    response_generator = ResponseGenerator(opts.input)
    if mode == 'tornado':
        application = tornado.web.Application([('/', JSONHandler)], debug=False)
        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
    elif mode == 'bottle':
        bottle.run(host='localhost', port=8888)
    elif mode == 'bottle-paste':
        bottle.run(server=bottle.PasteServer, host='localhost', port=8888)
    elif mode == 'bottle-cherry':
        bottle.run(server=bottle.CherryPyServer, host='localhost', port=8888)
    else:
        assert False
