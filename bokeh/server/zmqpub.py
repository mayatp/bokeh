from __future__ import absolute_import, print_function

import logging
log = logging.getLogger(__name__)

from threading import Thread

import json
from six.moves.queue import Empty
import zmq

timeout = 0.1

class Publisher(object):
    def __init__(self, zmqaddr, queue):
        self.zmqaddr = zmqaddr
        self.queue = queue
        self.kill = False

    def run(self):
        log.debug('zmqpub starting: %s' % self.zmqaddr)
        ctx = zmq.Context()
        socket = ctx.socket(zmq.PUB)
        log.debug('PUB CONNECT: %s' % self.zmqaddr)
        socket.connect(self.zmqaddr)
        try:
            while not self.kill:
                try:
                    message = self.queue.get(timeout=timeout)
                    socket.send_string(str(message))
                except Empty:
                    pass
        finally:
            socket.close()
        log.debug('zmqpub exiting')
    def send(self, topic, msg, exclude=[]):
        msg = json.dumps({'topic' : topic,
                          'msg' : msg,
                          'exclude' : list(exclude)})
        self.queue.put(msg)

    def start(self):
        self.thread = Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.kill = True
        if hasattr(self, 'thread'):
            self.thread.join()
