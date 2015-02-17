============
Introduction
============

This tutorial will use the `current µVM specification
<https://github.com/microvm/microvm-spec/wiki>`__ and the `µVM reference
implementation version 2 <https://github.com/microvm/microvm-refimpl2>`__.

The goal of the reference implementation is to make a **simple** µVM
implementation and allow early evaluators to do experiment with the interface of
the µVM. Since the µVM is still under heavy designing, the simplicity allows the
µVM refimpl to be agilely when the specification changes. It is **not** a
high-performance implementation. It is interpreted and single-threaded, does
excessive checking and is very slow.

Getting Started
===============

The current µVM reference implementation is written in Scala and runs on any JVM
(in theory. I only tested on Oracle JVM 1.8). If you are not familiar with
Scala, `this list <http://www.scala-lang.org/documentation/books.html>`__
provides useful resources and some books are freely available online.

Please follow the instructions in the `README
<https://github.com/microvm/microvm-refimpl2/blob/master/README.md>`__ file in
the ``microvm-refimpl2`` repository to install building tools, clone the
repository and build it.

It is recommended to use the ScalaIDE. It is the Eclipse IDE with Scala plugins
pre-installed. If you use IntelliJ IDEA, you may notice that it rejects some
correct Scala programs and accepts some Scala code with syntax/semantic errors.

The microvm-refimpl2 depends on Antlr4 to generate a parser. Make sure you
follow the instructions in the README file to generate extra source files and
let your IDE know their presence.

Run Some Tests
==============

There are some test suites in the ``src/test/scala`` directory (e.g.
``src/test/scala/uvm/refimpl/itpr/UvmInterpreterSpec.scala``). You can run them
using your favourite tool (e.g. the Eclipse IDE) to see if the µVM works
correctly. If it does, there should be no fails or errors.

.. vim: tw=80
