Simple cluster framework for python using ZMQ and cloudpickle
=============================================================

Introduction
------------

zero-cluster is a very minimal toolkit, intended for non-critical day to day cluster
tasks. It is composed of only three files. One library support file `zerocluster.py` and
two scripts `worker` and `router`.

Features and Limitations
------------------------
- Tasks instances and minimal dependencies are deployed to worker automatically at runtime.
- Supports deployment of class instances and functions
- Same instance of class is used for later invocation. Allows remote state between calls (example DB Connections)
- Python 2 and 3 Compatible, but can not be intermixed.
- No error handling (Disconnects, delivery guarantees)


Example Task:
-------------
```python
import zerocluster

class AddService:
    def add(self, x, y):
        return x + y

cluster = zerocluster.init('tcp://host:8989')
service = cluster.deploy(AddService())

job = service.add(1,2)
job.wait()
print(job.result())
```

Setup and Running:
-----------------
1. Install `pyzmq`, `cloudpickle` on all nodes of the cluster
2. Copy `worker` script to all nodes of the cluster
3. Run `router` script at `host` machine
4. Run `worker` script at all nodes of the cluster
5. Run tasks (see example above)

Dependencies
------------
- `pip install pyzmq`
- `pip install cloudpickle`


TODO
-----------------------------
- Error handling
- Complete example/test script
- Allow decorators for auto deployment
- Fine grained dependency deployment (Currently using cloudpickle's __main__ hack)
- Scripts to start/stop remote workers (SSH and kill signals)
- Notification of disconnects (Heartbeats) , retry policies for remote workers
- Task expirations on router and workers
- Policy based result retention and transfers. Currently using ZMQ defaults.
- Fine grained logging
- Task cancellation
