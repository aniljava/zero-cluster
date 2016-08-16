Simple cluster framework for python using ZMQ and cloudpickle
=============================================================

Introduction
------------

zero-cluster is a very minimal toolkit, intended for non-critical day to day cluster
tasks. It is composed of only three files. One library support file `zerocluster.py` and
two scripts `worker` and `router`.

Features
--------
	- Tasks instances and minimal dependencies are deployed to worker automatically at runtime.
	- Supports deployment of class instances and functions
	- Same instance of class is used for later invocation. Allows remote state between calls (example DB Connections)



Example Task:
-------------

    import zerocluster
    
    class AddService:
        def add(self, x, y):
            return x + y
   
    cluster = zerocluster.init('tcp://host:8989')
    service = cluster.deploy(AddService())
    
    job = service.add(1,2)
    job.wait()
    print(job.result())


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


Features, Limitation and Todo
-----------------------------
- Python 2 and 3 Compatible, but can not be intermixed.
- Disconnects, Delivery assurance are not handled.


