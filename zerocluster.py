
from __future__ import print_function
import zmq
import cloudpickle as pickle
import types
import uuid
import sys

STATUS_ACTIVE = 0
STATUS_COMPLETED = 1
STATUS_ERROR = 2



def init(router):
    return ZeroCluster(router)

class ZeroCluster:
    def __init__(self, router):
        self.router = router
        self.context = zmq.Context.instance()
        self.connection = self.context.socket(zmq.DEALER)
        self.connection.connect(router)
        self.calls = {}


    def deploy(self, obj, name = None, modules = None):
        """ Returns a wrapped object that delegates call to remote and returns a future object"""
        if name is None:
            name = str(id(obj)).encode('ascii')
        else:
            name = name.encode('ascii')
        
        if obj.__class__.__module__ != '__builtin__':
            obj.__class__.__module__ = '__main__'
        encoded = pickle.dumps(obj)
        
        payload = [b'REGISTER', name, encoded]
        self.connection.send_multipart(payload)
        wrapper = Wrapper(self, obj, name)
        return wrapper

    def call(self, instance_id, fx_name, *args, **kws ):
        call_uid = str(uuid.uuid4()).encode('ascii')
        call_data = [
            call_uid,
            instance_id,
            fx_name,
            args,
            kws
        ]
        encoded = pickle.dumps(call_data)
        payload = [
            b'CALL',
            encoded
        ]
        self.connection.send_multipart(payload)
        future = CallFuture(call_uid, self)
        self.calls[call_uid] = future
        return future


    def recv_all(self):
        # Read all pending messages
        count = 0
        while True:
            events = self.connection.poll(0)
            if events == 1:
                message = self.connection.recv_multipart()
                self.process_message(message)
                count += 1
            else:
                return count

    def process_message(self, message):        
        command, payload = message
        if command == b'RESULT':
            call_uid, result = pickle.loads(payload)
            if call_uid in self.calls:
                future = self.calls[call_uid]
                future.set_result(result)
                del self.calls[call_uid]

        if command == b'EXCEPTION':
            call_uid, exception = pickle.loads(payload)
            if call_uid in self.calls:
                future = self.calls[call_uid]
                future.set_exception(exception)
                del self.calls[call_uid]



    def poll(self, timeout=0):
        count = self.recv_all()
        if count == 0:
            events = self.connection.poll(timeout)
            if events == 1:
                self.recv_all()



class CallFuture:
    def __init__(self, callid, server):
        self.callid = callid
        self.server = server
        self.status = STATUS_ACTIVE
        self.result_data = None
        self.exception = None

    def wait(self):
        while not self.done():
            self.server.poll(None)
        


    def done(self, timeout=0):
        if self.status == STATUS_COMPLETED:
            return True
        else:
            self.server.poll(timeout)
            return self.status == STATUS_COMPLETED or self.status == STATUS_ERROR

    def set_result(self, result):
        self.result_data = result
        self.status = STATUS_COMPLETED

    def set_exception(self, exception):
        self.exception = exception
        self.status = STATUS_ERROR

    def result(self):
        if self.status == STATUS_ACTIVE:
            self.server.poll(0)

        if self.status == STATUS_COMPLETED:
            return self.result_data

        if self.status == STATUS_ERROR:
            raise self.exception

class Wrapper:
    def __init__(self, server, obj, name = None):
        self.server = server
        self.wrapped = obj
        if name is None:
            name = str(id(obj)).encode('ascii')
        self.instance_id = name

    def __call__(self, *args, **kws):
        return self.server.call(self.instance_id, '__call__', *args, **kws)

    def __getattr__(self, name):
        if hasattr(self.wrapped, name):
            def attr_wrapper(*args, **kws):
                return self.server.call(self.instance_id, name, *args, **kws)
            return attr_wrapper
        print('ERROR: UNKNOWN ATTRIBUTE REQUESTED:', name)

