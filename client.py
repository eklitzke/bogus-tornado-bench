import optparse
import time
import tornado.httpclient
import tornado.httputil
import tornado.simple_httpclient

class ClientBenchmark(object):

    def __init__(self, client, io_loop, url='http://localhost:8888/'):
        self.client = client
        self.url = url
        self.count = 0
        self.response_times = []
        self.requests = 0
        self.io_loop = io_loop
        self.headers = tornado.httputil.HTTPHeaders({'Connection': 'close'})

    def handle_response(self, response):
        #print 'handle_response'
        self.count += 1
        self.response_times.append(1000 * (time.time() - self.time_start))
        if self.count < self.requests:
            self.run_once()
        else:
            self.io_loop.stop()
            self.response_times.sort()
            total = sum(self.response_times)
            print 'avg time was %f' % (total / len(self.response_times))
            print 'median time was %f' % (self.response_times[int(len(self.response_times) * 0.5)],)
            print '95th percentile time was %f' % (self.response_times[int(len(self.response_times) * 0.95)],)

    def run_once(self):
        #print 'run once'
        self.time_start = time.time()
        request = tornado.httpclient.HTTPRequest(self.url, headers=self.headers)
        self.client.fetch(request, self.handle_response)

    def run(self, requests):
        self.count = 0
        self.requests = requests
        self.run_once()

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-r', '--requests', default=10000, type='int', help='how many requests to make')
    parser.add_option('-s', '--simple', action='store_true', default=False, help='use simple_httpclient')
    opts, args = parser.parse_args()

    io_loop = tornado.ioloop.IOLoop.instance()
    if opts.simple:
        async_client = tornado.simple_httpclient.SimpleAsyncHTTPClient(io_loop=io_loop, max_clients=1)
    else:
        async_client = tornado.httpclient.AsyncHTTPClient2(io_loop=io_loop)
    bench = ClientBenchmark(async_client, io_loop)
    io_loop.add_callback(lambda: bench.run(opts.requests))
    io_loop.start()
