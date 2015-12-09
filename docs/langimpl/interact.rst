=================
Basic Interaction
=================

You are writing a Mu *client*, which controls the Mu micro VM via the `Mu client
interface
<https://github.com/microvm/microvm-spec/blob/master/uvm-client-interface.rest>`__,
usually simply called "the API".

In Scala, the class ``uvm.refimpl.MicroVM``, which implements the ``MuVM``
struct in the specification, represents a micro VM instance. You can start Mu by
creating a ``MicroVM`` instance::

    val microVM = new MicroVM()

Just as simple as this. The instance also internally allocates memory for its
heap. The default heap size is quite big, and is usually enough for experiment.

Mu Contexts
===========

The client more often interacts with the micro VM via "Mu context", or "MuCtx"
in the spec or ``uvm.refimpl.MuCtx`` in the refimpl. A MuCtx is a context
created from a MicroVM instance. It can hold Mu values for the client, access
the Mu memory, load bundles and let the client perform many tasks on Mu.

Why not directly do these things on the MicroVM instance? Why add another layer?

Mu is designed to be multi-threaded, and multiple client threads can interact
with the Mu micro VM concurrently. (Unfortunately the *reference implementation*
is single thread only. Do not run more than one client threads in the reference
implementation, but multiple Mu threads are interpreted on a round robin
scheduler.) When accessing one single object concurrently, there will be races,
and locks must be employed to make it thread-safe. For this reason, each client
thread will work on one or more MuCtx instances. A MuCtx cannot be used by two
threads concurrently. Usually operations, such as creating primitive Mu values,
do not need locking. A MuCtx instance can also hold a thread-local memory pool
so that a client thread can allocate memory without having to lock the global
memory pool every time, unless the local pool is exhausted. The MuCtx can also
hold references to Mu heaps so that the garbage collector can still scan those
references.

If you used JNI before, you may find this design familiar. In fact, this design
is inspired by the JNI. Just like the JVM, Mu also puts a lot of emphasis on
concurrency.

You can create a ``MuCtx`` instance by invoking the ``newContext()`` method on
the ``MicroVM`` instance::

    val ctx = microVM.newContext()

and you need to close the context in order to release the resources it is
holding inside::

    ctx.closeContext()

.. vim: tw=80
