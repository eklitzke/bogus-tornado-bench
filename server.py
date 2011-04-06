import optparse
import simplejson

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

class JSONHandler(tornado.web.RequestHandler):

    def get(self):
        self.set_header('Content-Type', 'application/json')
        response = self.application.response_generator.get_object()
        self.write(simplejson.dumps(response))

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', help='file of lines to input')
    opts, args = parser.parse_args()

    application = tornado.web.Application([('/', JSONHandler)], debug=False)
    application.listen(8888)
    application.response_generator = ResponseGenerator(opts.input)
    tornado.ioloop.IOLoop.instance().start()
