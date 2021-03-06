============
Introduction
============

The Mu project addresses the difficulties in implementing managed languages,
which include those languages that have a garbage collector and likely run on a
virtual machine.

What Makes Language Implementation Difficult?
=============================================

We identify three major concerns that make language implementation difficult, 
namely **concurrency**, **just-in-time compiling** and **garbage collection**.

Each of them is already difficult enough individually. But when handling all
three at the same time, their combined complexity will multiply.

    For example, in a multi-threaded JIT-compiled garbage-collected program,
    when GC is triggered, the GC thread needs to ask all mutator threads running
    in JIT-compiled machine code to pause at the nearest GC-safe points (or
    "*yieldpoints*"), where stack maps are available to identify all references
    held by variables in the stack. In this task, the yieldpoints are inserted
    by the JIT-compiler, which is aware of GC. The stack maps are generated by the
    JIT-compiler, too. The handshake between mutators and the GC is very
    difficult to get right, too. Yieldpoints involve all three concerns
    mentioned above.

Because they are difficult, language implementations either omit them or
implement them naively.

    Take CPython, the official Python implementation, as an example:

    + *lack of concurrency*: In CPython, there is a `global interpreter lock
      (GIL)
      <https://docs.python.org/3.4/glossary.html#term-global-interpreter-lock>`__
      which must be obtained for any Python thread to run. This makes the
      execution of all multi-threaded Python programs sequential.

    + *lack of JIT-compiling*: CPython is interpreter-only and does not perform
      run-time optimisation based on JIT-compiling and type inference. A simple
      computation-intensive program may be up to 20 times slower than an
      equivalent C program. For comparison, PyPy, a Python implementation that
      does JIT-based optimisation, can run as fast as unoptimised C (GCC with
      -O0) in some cases.

    + *naive garbage collector*: CPython uses a naive reference counting garbage
      collector. It increments or decrements the count every time a reference is
      created or destroyed. This naive algorithm is known to be `more than 30%
      slower than a naive mark-sweep GC in total execution time
      <http://users.cecs.anu.edu.au/~steveb/downloads/pdf/rc-ismm-2012.pdf>`__.

In reality, **many languages designs are implementation driven**. Difficulties
in implementation will result in **bad decisions being baked into the design**
and hamper the evolution of the language in the future.

    Take PHP as an example. PHP `was never supposed to be a programming language
    <http://en.wikipedia.org/wiki/PHP#cite_ref-itconversations_16-0>`__, but a
    set of pre-processing macros for personal home pages. As it evolves, it uses
    naive reference counting GC, copy-by-value semantic for arrays, and has
    reference types. An optimisation was also made to use copy-on-write to avoid
    copying.  In 2002, a user `found a problem involving arrays and references
    <https://bugs.php.net/bug.php?id=20993>`__. Fives days later, the PHP
    developers `decided that properly fixing the bug will put a considerably
    slowdown on the PHP performance
    <https://bugs.php.net/bug.php?id=20993#1040181945>`__ and this behaviour is
    documented.

    Up till now in 2015, it has been 12 years since the problem was spotted. The
    problem can still be reproduced in today's PHP.

In conclusion, concurrency, JIT and GC are difficult. The difficulties lead to
bad language designs and implementations, and should be abstracted out in a
layer.

Why Micro Virtual Machines?
===========================

There are basically two ways to implement a managed language.

1. Building a VM from scratch. This is difficult because the developers have to
   address all of the three concerns. In reality, there are many successful
   projects taking this approach, such as `PyPy <http://www.pypy.org/>`__, `HHVM
   <http://hhvm.com>`__, `V8 <https://developers.google.com/v8/>`__ and so on.
   Most don't address all three concerns, and no code is shared between those
   projects.

2. Targeting an existing virtual machine, such as the JVM or the .NET CLR, which
   has high-quality implementations. The problems are *semantic gaps* and *huge
   dependencies*. Existing VMs are designed for particular kinds of languages.
   For example, the JVM is designed for static object-oriented languages.
   Optimisations usually done by JVM do not work for dynamic languages like
   Python.  `Jython <http://www.jython.org/>`__, for example, still performs in
   the same order of magnitude as CPython. Moreover, using JVM introduces many
   unnecessary dependencies on Java-related packages.

Both approaches use **monolithic virtual machines**. Each such VM handles all
aspects of the runtime of the language. For example, the JVM handles
concurrency, JIT and GC, but also class loading, run-time type information,
object-oriented programming (including virtual methods), and it comes with a
comprehensive Java standard library. Since the VM is huge, it is difficult to
build from scratch. Since it is monolithic, it is difficult to reuse its parts
for other languages.

We propose an alternative concept: **micro virtual machines**. Analogous to
*microkernels* in the operating system literature, a micro virtual machine only
contains the parts that are absolutely necessary to be handled in the core of
the VM. We suppose those parts are concurrency, JIT and GC. There is a separate
program, called a **client**, sitting on the top of a micro virtual machine,
interacting with the micro virtual machine and handling other (mostly
language-specific) parts, in a similar fashion as *servers* interacting with the
microkernel.

A micro virtual machine must be **low-level** and **minimal**.

* Being low-level means being close to the machine and thus minimise the
  semantic gap.

* Being minimal means it must push jobs that are not essential to the higher
  level, that is, the client. This is a separation of concern.
  
  - The micro virtual machine itself will be easier to design and implement. The
    minimalism also makes it practical to create a formally verified VM.

  - The client is not bound to the assumptions made by the low-level VM and can
    implement the language with maximum flexibility. The client has more
    responsibility, too, but it can still rely on the micro virtual machine for
    the three major concerns that are extremely difficult.

The minimalism pushes as much job as possible to the client side, potentially
making the language implementer's job harder than targeting traditional VMs like
JVM. To mitigate this limitation, **libraries** can be provided to assist the
implementation of certain kinds of languages, like dynamic languages, functional
languages, object-oriented languages and so on. Libraries are *not* part of the
micro virtual machine. The library can be a framework or a package that is part
of the client; it can also be pre-written code snippets.

The **Mu** project is a concrete micro virtual machine, in the same way `seL4
<http://sel4.systems/>`__ is a concrete microkernel.

Separating the Specification and the Implementation
===================================================

Mu separates its specification and its implementations, making it possible to
create many different implementations for different purposes.  In theory, there
may be a simple proof-of-concept implementation, a high-performance
implementation for productional use, an extensible modular implementation for
researching, a formally verified implementation for highly-assured
applications, and so on.

The `Mu specification <https://gitlab.anu.edu.au/mu/mu-spec>`__ defines the
behaviour and the interface of Mu.

Currently, Mu has two implementations:

- `Holstein <https://gitlab.anu.edu.au/mu/mu-impl-ref2>`__, the reference
  implementation, is a **simple** Mu implementation and allow early evaluators
  to do experiment with the interface of Mu.  The simplicity allows Mu reference
  implementation to be agilely changed when the specification changes. It is
  **not** a high-performance implementation.

- `Zebu <https://gitlab.anu.edu.au/mu/mu-impl-fast/>`__, the fast
  implementation, is developed from the first day to be **fast**.  It is written
  in Rust, and has a optimizing compiler and a high-performance garbage
  collector.  It is currently implemented as an ahead-of-time compiler.  Some
  functionalities are still in development.

.. vim: tw=80
