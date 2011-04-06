import optparse
import time
import tornado.httpclient

class ClientBenchmark(object):

    def __init__(self, client, io_loop, url='http://localhost:8888/'):
        self.client = client
        self.url = url
        self.count = 0
        self.response_times = []
        self.requests = 0
        self.io_loop = io_loop

    def handle_response(self, response):
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
        self.time_start = time.time()
        self.client.fetch(self.url, self.handle_response)

    def run(self, requests):
        self.count = 0
        self.requests = requests
        self.run_once()

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-r', '--requests', default=10000, type='int')
    opts, args = parser.parse_args()

    io_loop = tornado.ioloop.IOLoop.instance()
    async_client = tornado.httpclient.AsyncHTTPClient2(io_loop=io_loop)
    bench = ClientBenchmark(async_client, io_loop)
    io_loop.add_callback(lambda: bench.run(opts.requests))
    io_loop.start()
