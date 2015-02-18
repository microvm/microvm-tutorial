===============
Getting Started
===============

Where is Everything?
====================

The `specification <https://github.com/microvm/microvm-spec/wiki>`__ is the
canonical source of information about the implementation-neutral parts of the
µVM.

This tutorial will use the `reference implementation
<https://github.com/microvm/microvm-refimpl2>`__. Keep in mind that it is not
high-performance. It is interpreted and single-threaded, does excessive
checking and is very slow.

The current µVM reference implementation is written in Scala and runs on JVM
1.8 (tested on HotSpot). If you are not familiar with Scala, `this list
<http://www.scala-lang.org/documentation/books.html>`__ provides useful
resources and some books are freely available online.

Get the µVM
===========

Please follow the instructions in the `README
<https://github.com/microvm/microvm-refimpl2/blob/master/README.md>`__ file in
the ``microvm-refimpl2`` repository to install building tools, clone the
repository and build it.

It is recommended to use `ScalaIDE <http://scala-ide.org/>`__. It is the Eclipse
IDE with Scala plugins pre-installed. If you use IntelliJ IDEA, you may notice
that it rejects some correct Scala programs and accepts some Scala code with
syntax/semantic errors.

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
