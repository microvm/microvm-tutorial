=======================
Interacting With the Mu
=======================

The client interacts with Mu in two ways: the *Mu IR* and the *Mu client
interface*.

Mu Intermediate Representation
===============================

The code which Mu reads and executes is called the **Mu Intermediate
Representation**, or **Mu IR** for short.

The Mu IR is `defined by the Mu specification
<https://github.com/microvm/microvm-spec/wiki/uvm-ir>`__.

Example Mu IR code
------------------

The unit of code delivery to Mu is **bundle**.

Here is an example bundle in the text format: ``tests/tutorial/interact.uir``

.. literalinclude:: code/interact.uir
    :language: uir
    :linenos:

Structure of a Bundle
---------------------

A bundle has many **top-level definitions**.

Top-level definitions begin with a word starting with a dot "``.``". For
example, ``.typedef @i64 = int<64>`` defines a type: 64-bit integer, and binds a
name ``@i64`` to that type. Similarly, ``.typedef @void = void`` binds the name
``@void`` to the void type.

    You can even bind more than one names to the "same" type. When referred to
    later, ``@void``, ``@just_another_void``, ``@still_void`` will not have any
    noticeable difference from the client's point of view. (Of course from the
    Mu implementer's point of view they are somewhat different)

Similarly, ``.const``, ``.global``, ``.funcsig``, ``.funcdef``, ``.funcdecl``
define constants, global cells, function signatures, functions and function
versions, and also give them names.

    Notes about the term "*function version*": Functions in Mu may have
    multiple versions. They will be introduced later. For now, just remember
    that a function version is the body of a function. Every ``.funcdef``
    defines a "function version". 

In the Mu IR, every **identified entity** must have an ID and optionally a name.
In Mu, *types*, *function signatures*, *constants*, *global cells*, *functions*,
*function versions*, *parameters*, *basic blocks* and *instructions* are
identified entities.

An ID is a 32-bit integer. ID is not used in the text form of the IR. It will be
automatically assigned.

There are **global names** (start with ``@``) and **local names** (start with
``%``). Local names are simply for the convenience of writing. It is exactly
equivalent to ``@func_ver_name.local_name`` where ``func_ver_name`` is the name
of the function version (not including the ``@``) and ``local_name`` is the
local name (not including the ``%``). For example, the name ``%body`` in
``@gcd_v1`` is equivalent to ``@gcd_v1.body``, and ``%b1`` is equivalent to
``@gcd_v1.b1``.

**Both IDs and names uniquely identify entities.**

Inside a function definition, there are many basic blocks. The first block is
the "entry block" and is conventionally named ``%entry``. Each basic block has
many instructions.

    If you worked with LLVM before, you may find it very familiar. Indeed Mu is
    inspired by the LLVM. It also uses the SSA form.

Each instruction performs a certain computation. Consider the line:

.. code-block:: uir

    %b1 = SREM <@i64> %a %b

``%b1`` is the name of the instruction. If this name is referred to by another
instruction, it is referring to the result produced by that instruction. For
this reason, ``%b1`` can also be interpreted as "a variable that holds the
result of that instruction". Anyway, there is always a one-to-one mapping
between instructions and their results.

The ``TRAP`` Instruction
------------------------

One instruction needs special attention at this moment: the ``TRAP``
instruction. From time to time, the program written in the Mu IR will need to
handle events which Mu cannot handle alone. The ``TRAP`` is like a special jump.
It transfers the control from the Mu IR program to the client. A registered
*trap handler* in the client will handle such an event.

This is so far you need to know about Mu IR.

    Exercise: Write a program and load the bundle above into a Mu instance.

Mu Client Interface
====================

The client not only submits bundles to Mu, but also directly controls Mu
directly via the **Mu client interface**, which is also simply called **the
API** if not ambiguous.

The interface is two-way: the client can send messages to Mu to manipulate its
state; Mu calls back to the client to handle events which Mu cannot handle by
itself (including the execution of a ``TRAP`` instruction). 

The specification defines the `messages in the API
<https://github.com/microvm/microvm-spec/wiki/uvm-client-interface>`__.

In the reference implementation, Mu itself is represented by a
``uvm.refimpl.MicroVM`` instance. Most messages are sent to Mu via a
``uvm.refimpl.ClientAgnet`` instance.

Loading a Bundle
----------------

In this example, we will create a Mu instance and a client agent:

.. code-block:: scala

    import uvm.refimpl._

    val microVM = new MicroVM()
    val ca = microVM.newClientAgent()

Assume the above bundle is saved in ``tests/tutorial/interact.uir``. Let's load
it into Mu:

.. code-block:: scala

    val reader = new java.io.FileReader("tests/tutorial/interact.uir")
    ca.loadBundle(reader)
    reader.close()

The ``ca.loadBundle`` method takes a Java ``Reader`` and loads the bundle from
it in the text form. Now the bundle is loaded into Mu.

But nothing will happen because you did not tell Mu to run anything.

Threads and Stacks
------------------

In Mu, a **thread** is an abstraction of a virtual processor that is
capable of executing code. It is the unit of scheduling and is *usually*
implemented as one-to-one mapped to OS threads. In this reference
implementation, however, threads are implemented as green threads, that is, one
single Java thread executing instructions for multiple Mu threads, one
instruction at a time, alternating between all Mu threads.

But a thread alone is not enough. It needs a context to execute on. In Mu,
a **stack** is the context in which a thread executes. A stack contains many
**frames**, each of which contains the context of a function activation. A frame
contains an instruction pointer to indicate which instruction is being executed,
the value of all local variables in a function, and memory cells explicitly
allocated on the stack.

To execute a Mu function, the client should create a new Mu stack with a frame
containing the context of the desired Mu function, and create a new Mu thread
that binds to that stack. Then the thread keeps executing in the context of the
stack until it hits a special instruction ``@uvm.thread_exit``.

    NOTE: If you have worked with threads in other programming languages, for
    example, C with POSIX threads, Java, Python and so on, you may find the
    concept *stack* a bit alien. In those interfaces, when you create a new
    thread, a new stack is implicitly created for that thread, and the stack
    will accompany the thread until the thread exits. Some interfaces, for
    example POSIX threads, does allow the programmer to manually allocate the
    stack memory.

    In Mu, however, the relationship between a thread and a stack is not fixed.
    A thread may unbind from a stack and rebind to another stack, making it a
    kind of explicit light-weight context switching implemented within Mu.
    Traps also make use of the same mechanism to switch context from a Mu
    program to the client. This will be discussed in greater depth in the
    future.

    From the physical processor's point of view, a stack is a piece of memory
    referred by a special register, for example ``RSP`` in x86_64. Changing the
    value of this register will allow the processor to execute on a different
    context. This usually happen during system calls and signal handling.

Now let's create a stack with the context of the ``@main`` function.

.. code-block:: scala

    val mainFuncID : Int     = microVM.idOf("@main")
    val mainFunc   : Handle  = ca.putFunction(mainFuncID)
    val st         : Handle  = ca.newStack(mainFunc, Seq())

Most Mu-client API messages use the ID to identify entities, because that is
what should be implemented in a realistic environment, in which the binary form
Mu IR is used rather than the text form. The ``microVM.idOf`` method looks up
the ID of a given name.

A **handle** is an opaque representation of a Mu value held by the client
agent. In this case, the ``ca.putFunction`` message asks the client agent to
create a Mu value, which is function reference value referring to the ``@main``
function. This value is held by the client agent ``ca``, and it is exposed to
the client as the handle ``mainFunc``. Similarly the ``ca.newStack`` message
tells the client agent to create a new Mu stack, with a frame for the main
function with an empty argument list ``Seq()``. The returned value is a Mu
stack reference, referring to the new stack, and it is exposed to the client as
the handle ``st``.

    There are two reasons why Mu exposes Mu values to the client via opaque
    handles rather than raw values.

    1. There is a gap between the type system of Mu and the type system of the
       language the client is written in. In this case, it is the Mu type
       system and the Scala type system. Mu may have types which the client
       language cannot represent. For example, Mu allows integers of some
       weird lengths (for example, integers of 52 bits) which is not
       supported by most languages.  If the client is written in C, it does
       not have reference types. Mu also has opaque types which the
       representation is a detail of a particular Mu implementation. This
       opaque approach bridges the gap between the two type systems.

    2. Mu needs to keep track of all references to the Mu heap in order to
       perform exact garbage collection. This is trivial if all references
       exposed to the client are indirect handles via the client agent. For
       implementations which does not move objects, the handle can be the raw
       pointer itself, but the client simply does not know this fact and is not
       supposed to rely on it.

To make your Scala program more concise, you can define an implicit conversion
function that transparently does ``microVM.idOf`` for you. A more concise
version can be:

.. code-block:: scala

    implicit def idOf(name: String) = microVM.idOf(name)

    val mainFunc = ca.putFunction("@main") // implicitly converting "@main" to its ID
    val st = ca.newStack(mainFunc, Seq())

Then we create a Mu thread.

.. code-block:: scala

    val th = ca.newThread(st)

As you may have guessed, the ``ca.newThread`` message tells the client agent to
create a new Mu thread, using the stack ``st`` as its context, and return a
thread reference, exposing it to the client as the handle ``th``.

Now the thread ``th`` will run on the stack ``st``. As you have created your
thread, you may close the client agent now. This will destroy all the handles
you created using this client agent and free the resources held by the client
agent.

.. code-block:: scala

    ca.close()

Unfortunately the program still does not run! That's because the current Mu
reference implementation is single-threaded. You must tell Mu to run itself in
the current thread, that is, the "main thread", that is, the Java thread in
which all code so far has run.

.. code-block:: scala

    microVM.threadStackManager.joinAll()

Then it runs... until it throws an exception similar to this::

    Unhandled trap. Thread 1, funcver [65555:@main_v1], trap inst [65558:@main_v1.the_trap]

That's normal. It actually ran, but when executing the ``TRAP`` instruction in
the ``@main`` function, Mu asks the client for help by attempting to call a
registered trap handler. But the default trap handler simply throws an
exception when called.

Trap Handler
------------

Let's register a handler before letting Mu run again.

.. code-block:: scala

    object MyTrapHandler extends TrapHandler {
      def handleTrap(ca: ClientAgent, thread: Handle, stack: Handle, watchPointID: Int): TrapHandlerResult = {
        val curInstID = ca.currentInstruction(stack, 0)
        microVM.nameOf(curInstID) match {
          case "@main_v1.the_trap" => {
            val Seq(result) = ca.dumpKeepalives(stack, 0)
            val resultInt = ca.toInt(result, signExt = true)
            printf("The result is %d.\n", resultInt)
            TrapRebindPassVoid(st)
          }
        }
      }
    }
    
    microVM.trapManager.trapHandler = MyTrapHandler

When the ``TRAP`` instruction is executed, Mu temporarily unbinds the
thread from the stack, leaving the stack available for introspection. Pay
attention to the ``KEEPALIVE`` clause in the ``TRAP`` instruction:

.. code-block:: uir
    :emphasize-lines: 3

    %result = CALL <@BinaryFunc> @gcd (@I64_18 @I64_12)

    %the_trap = TRAP <@void> KEEPALIVE(%result)
    
Consider that the code generator of a highly-optimising Mu implementation may
perform liveness analysis and discard the value of some variables if it is never
used again (i.e. "dead" variables). Not all variables may be "alive" when the
``TRAP`` instruction is executed, so their values may not always be available
for introspection. To solve this problem, all variables whose value are supposed
to be introspected must be explicitly declared in the ``KEEPALIVE`` clause, and
exactly those variables in the ``KEEPALIVE`` clause can be introspected by the
client.

    Question: Do I need to declare all variables? I am certain that some
    variables must be alive at the point of the trap.

    Answer: Yes. First of all, it was the client that generated the function. The
    client has full knowledge about what is the purpose of the trap and which
    variable should be introspected. Being explicit simply makes things easier.
    Secondly the client does not need to depend on how aggressively Mu optimises
    the code. Although Mu is supposed to perform minimal work and push much job
    to the client, the client still cannot assume how minimal Mu is.

Before entering the trap handler, Mu already created a temporary client
agent for the client, having the handles of the thread and the stack already
available. These are provided by the parameters of the ``handleTrap`` method.
You can temporarily ignore the ``watchPointID`` parameter for now. The client
agent will be automatically closed upon returning from the trap handler.

The first thing the client should do is to test **which** ``TRAP`` instruction
is executed because there may be more than one traps in the code in all the
bundles Mu has loaded. As stated before, *the name uniquely identifies an
entity*. We first use the ``ca.currentInstruction`` message to obtain the ID of
the current instruction, which is the ``TRAP`` instruction. Then we let Mu
translate the ID to the textual name using the ``microVM.nameOf`` method. The
name will be the *global name* (starting with ``@``, in the form of
``@func_ver_name.local_name``). Then we match the name against all names of
known traps.

Currently we only know about one trap, which is ``@main_v1.the_trap``. We dump
the value of all variables in the ``KEEPALIVE`` clause by ``ca.dumpKeepalives``,
which returns a sequence of handles. This allows the client to introspect the
value of the designated local variables, in this case it is only the ``%result``
variable.  Since we know ``%result`` holds an integer value, we convert the
handle to a Scala ``BigInt`` by ``ca.toInt`` and also tells it to sign-extend
the Mu integer value because it is supposed to be signed. Then we print the
value using the good old ``printf`` method.

    Note: In Mu, an integer type only has length, but not signedness.  Concrete
    operations may treat an integer value as signed or unsigned. This will be
    discussed later.

The last thing to do before leaving the trap handler is to decide how the thread
should continue. Killing the thread is a good idea here, but this time we choose
to rebind the thread with the old stack. This is achieved by returning
``TrapRebindPassVoid(st)`` which rebinds the thread with the old stack ``st``.

After returning from the trap handler, the Mu program continues from the
``TRAP`` instruction and hits the "common instruction" ``@uvm.thread_exit``
which stops the thread and automatically destroys the stack.

    Note: "Common instruction" is just a fancy name of all instructions that
    follows a certain format. It is introduced to make the Mu IR extensible,
    that is, it allows introducing new instructions without modifying the
    parser.

To put them all together, we have this file
``src/test/scala/tutorial/Interact.scala``:

.. literalinclude:: code/Interact.scala
    :language: scala
    :linenos:

Run this program and you will see this line among other logs::

    The result is 6.
    
In this way, the Mu program is executed and the result is printed to the
console with the help of the client, that is, your Scala program.

Recap
=====

The client interacts with Mu in two ways: the **Mu IR** and **the API**.

The Mu IR contains many top-level definitions. Specifically, in a function
definition, it uses the same SSA form as LLVM, having multiple basic blocks each
having many instructions.

Every entity in the Mu IR is identified by an ID and optionally a name. The
local name is just a shorthand of its global counterpart. Both IDs and names can
uniquely identify an entity.

The ``TRAP`` instruction is special. It transfers the control to the client for
doing things Mu cannot do alone.

The API allows the client to manipulate the state of Mu, and also respond to
traps.

Mu only exposes opaque handles to the client rather than raw values. It is
for segregating the difference between the type system of the client and
Mu, and to facilitate exact garbage collection. However, simple values,
including integers, floating point numbers and vectors, can be converted to and
from the client's native values in restricted ways.

To start a Mu program, the client should create a stack with the context of a
function, and a thread using the stack as its context. All of them are done with
the help of a client agent.

The trap handler gives the client a chance to introspect the state of the
execution of a Mu thread. It can introspect the value of "keepalive" variables
and decide how the thread should continue.

.. vim: tw=80
