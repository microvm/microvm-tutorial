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
There are two reasons.

Reason 1: because Mu is designed to be **multi-threaded**. By design, multiple
client threads can interact with the Mu micro VM concurrently.

.. caution::

    In fact, unfortunately, the *reference implementation* is based on a
    single-thread interpreter. The program itself is **not thread safe**. Do not
    run more than one *client threads* in the reference implementation.

    But Mu is designed for multi-threaded envirionments. The limitation in the
    implementation does not change the fact that Mu and its clients need to
    think in a multi-threaded way. A carefully designed interface will
    eventually allow a more efficient implementation. 
    
    Despite this limitation, the reference implementation can still run multiple
    **Mu threads**. Mu threads are interpreted one instruction for each thread
    on a round robin scheduler.

If multiple client threads were accessing the single MicroVM object
concurrently, synchronisation (such as locks) must be employed to guarantee
thread safety. This is where the "context" comes in. In Mu's design, MuCtx
instances are not allowed to be used by two threads concurrently, thus avoided
many cases where synchronisation were necessary. For example, accessing the
garbage-collected Mu memory via MuCtx does not need locking. A MuCtx instance
can also hold a thread-local memory pool so that a client thread can allocate
memory in the garbage-collected Mu heap without having to deal with the shared
global memory pool every time unless the local pool is exhausted.

Reason 2: because the *type system* of Mu is usually very different from the
client's. Notably, the Mu's type system contain **object reference** types which
points to the Mu heap and **must be traced by the garbage collector**. MuCtx can
hold Mu references for the client so that whenever garbage collection happens,
it always knows what objects are still kept alive by a reference held for the
client.

If you used JNI before, you may find this design familiar. In fact, this design
is inspired by the JNI. JNI uses opaque "handles" to refer to Java object, so
does the Mu API. However, for performance reason, opaque handles are not the
only way to expose garbage-collected Mu objects to *native* programs. Mu has a
more efficient but unsafe `native interface
<https://github.com/microvm/microvm-spec/blob/master/native-interface.rest>`__
which supports "object pinning". That is an advanced topic.

.. note::

    There is a difference between a **Mu client** and a **native program**.
    
    A Mu client is a program that controls the Mu micro VM. In theory, a Mu
    client can be written in any languages, from C to Scala, Python, JavaScript,
    etc. The Mu API is the interface between the *client* and the *micro VM*. It
    includes the IR and the API, and the purpose is to control the micro VM.

    A native program is a program that does not run in the Mu micro VM, and is
    usually written in C or other unmanaged languages. libc is one such example.
    The native interface involves pointer-based raw memory access and calling
    conventions that allow Mu programs to call C programs and vice versa in some
    specific ways.  The main purpose is to make system calls (obviously a VM
    that cannot ``read`` or ``write`` is almost useless), and to interact with
    programs that do not run on Mu, including C programs and those written in
    other languages.

Using Mu Contexts
-----------------

You can create a ``MuCtx`` instance by invoking the ``newContext()`` method on
the ``MicroVM`` instance::

    val ctx = microVM.newContext()

and you need to close the context in order to release the resources it is
holding inside::

    ctx.closeContext()

The following code is an overview of what the client context can do. These API
functions are defined by the `specification
<https://github.com/microvm/microvm-spec/blob/master/uvm-client-interface.rest>`__,
and the `scala binding
<https://github.com/microvm/microvm-refimpl2/blob/master/src/main/scala/uvm/refimpl/clientInterface.scala>`__
matches the spec. You don't need to understand all of them now, since they will
be covered in more depth in later chapters.

.. code-block:: scala

    val microVM = new MicroVM()
    val ctx = microVM.newContext()

    // Mu context can load bundles.
    ctx.loadBundle("""
        .typedef @i64 = int<64>
        // more Mu IR code here
    """)

    // It can hold Mu values for the client. Mu values have a specific int size.
    val handle1 = ctx.handleFromInt(0x123456789abcdef0L, 64)
    val handle2 = ctx.handleFromInt(0x12345678L, 32)
    val handle3 = ctx.handleFromInt(0x1234L, 16)
    val handle4 = ctx.handleFromDouble(3.14)
    val handle5 = ctx.handleFromPtr(ctx.idOf("@someType"), 0x7fff0000018L)

    // It can allocate objects in the Mu heap.
    // The handle is held in ctx so that GC can find all of them.
    val handle6 = ctx.newFixed(ctx.idOf("@someType"))
    
    // It can create stacks and threads
    val hFunc   = ctx.handleFromFunc(ctx.idOf("@some_function"))
    val hStack  = ctx.newStack(hFunc)
    val hArg0   = ....
    val hArg1   = ....
    val hArg2   = ....
    val hThread = ctx.newThread(hFunc, PassValues(Seq(hArg0, hArg1, hArg2)))

    // It can access the Mu memory
    val hObjRef = ctx.newFixed(ctx.idOf("@int_of_64_bits"))
    val hIRef   = ctx.getIRef(hObjRef)
    val hValue  = ctx.load(MemoryOrder.SEQ_CST, hIRef)

    // It can introspect the stack states
    val hStack2 = .....
    val hCursor = ctx.newCursor(hStack2)
    val funcID  = ctx.curFunc(hCursor)          // function ID
    val hVars   = ctx.dumpKeepalives(hCursor)   // local variables

    // It can modify the stack states
    ctx.nextFrame(hCursor)
    ctx.popFramesTo(hCursor)
    val hFunc2  = ctx.handleFromFunc(...)
    ctx.pushFrame(hFunc2)
    
Threads and Stacks
==================

Mu programs are executed on Mu threads. A thread is the unit of CPU scheduling,
and Mu threads are usually implemented mirroring operating system threads.
Multiple Mu threads may execute concurrently.

Each Mu thread runs on a Mu **stack**. A stack, commonly known as a *control
stack*, is the state of execution, represented in Mu as a list of *frames*. Each
frame corresponds to a Mu function version, and records which instruction should
be executed next and what are the values of local variables.

Mu clearly distinguish between threads and stacks. If you used traditional
thread APIs, such as the Java or the PThread API, you may already have the
mental model that "a thread has a stack, which has many frames, so threads and
stacks are interchangeable". But in Mu, the relation of stacks and threads is
much more flexible. A thread can stop executing on one stack and resume another
stack, which gives "coroutine" behaviours. Multiple threads can also share a
much bigger stack pool and implement the M*N threading model.

In order to start executing a Mu program, the client should create a Mu stack
and a Mu thread. In order to stop executing, the Mu thread should execute the
``@uvm.thread_exit`` instruction.

Trap Handling
=============

There is one special instruction, ``TRAP``, that needs special attention since
the beginning. During the execution of Mu programs, if a Mu thread executes a
``TRAP`` instruction, the thread temporarily detaches from its stack and gives
control back to the client. At any moment, there is one trap handler registered
in a Mu instance. A trap handler is a client function that will be called
whenever a ``TRAP`` instruction is executed. The trap handler gains access to
the thread and the stack that caused the ``TRAP``.

Using the API, the client can to introspect the execution state of each of its
frames, see the values of local variables, and even replace existing frames with
new frames for new functions (this is called on-stack replacement, or OSR).

The trap handler is a great opportunity for the client to do many things. The
clever placement of ``TRAP`` instructions and the implementation of the trap
handler is key to a good language implementation. Traps can be placed after
sufficient run-time statistics are collected so that the client can optimise the
program. Traps can also be used for lazy code loading, de-optimising
speculatively generated code, and debugging.

TODO: how to register trap handlers

Working Example
===============

TODO

Summary
=======

* A MicroVM instance is the heart of the Mu micro VM.

* The client interacts with the micro VM mostly via MuCtx. A context serves only
  one client thread. It holds Mu values, including garbage-collected object
  references.

* In Mu, threads and stacks are loosely coupled. Threads can swap from one stack
  to another.

* The ``TRAP`` instruction gives the control back to the client from an
  executing Mu thread.

* To start everything: create a MicroVM, create a MuCtx, load a bundle, create a
  stack and create a thread. The ``MicroVM.execute()`` API function is specific
  to the reference implementation.

.. vim: tw=80
