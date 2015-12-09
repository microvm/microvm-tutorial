===============
Getting Started
===============

Where is Everything?
====================

The `specification <https://github.com/microvm/microvm-spec/wiki>`__ is the
canonical source of information about the implementation-neutral parts of Mu.

This tutorial will use the `reference implementation v2
<https://github.com/microvm/microvm-refimpl2>`__. Keep in mind that it is not
high-performance. It is interpreted and single-threaded, does excessive checking
and is very slow.

Get Mu
======

Go to https://github.com/microvm/microvm-refimpl2/ and follow the README file.
That repository also contains a sample factorial program compiled from an
RPython client and a loader to run it. Read the README file.

Pick your language
==================

The client of the reference implementation can be written in Scala or in C. If
you use Scala, you can just use the classes in the ``microvm-refimpl2``
repository since the reference implementation is already written in Scala. If
you use C, there is a C binding in the ``cbinding`` directory. Read the README
file for instructions. There is also a sample client program ``test_client``.

The following part of the tutorial assume you use Scala. Don't worry if you use
C because the interface is quite similar.

.. vim: tw=80
