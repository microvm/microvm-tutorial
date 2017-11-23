===========
Type System
===========

The Mu type system is defined in `the specification
<https://gitlab.anu.edu.au/mu/mu-spec/blob/master/type-system.rst>`__.

Like many programming languages and frameworks, Mu also has a type system.

The Mu type system is low level. There is no object-oriented programming
concepts, such as class, inheritance, polymorphism. There is no high-level
concepts such as strings, either. The language implementer is responsible to
implement these high-level concepts.

But the Mu type system is also not too low level. Notably, unlike C, C++ or
LLVM, the Mu type system still has object reference types in it, and the garbage
collector is fully aware of the presence of them. The main idea is, as long as
you use the Mu type system, and refer to heap objects using references, you can
forget about garbage collection details, such as stack maps, GC-safe points, and
read/write barriers.

Overview
========

Some of the types (actually :ref:`type constructors <type-constructor>`,
explained later) contain angular brackets. These are parameters to these types
which may be integer literals, other types or function signatures.

The types in the Mu type system can be put into several categories:

1. Scalar value types: ``int<n>``, ``float``, ``double``, ``uptr<T>`` and
   ``ufuncptr<sig>``. These types represent plain values.

2. Scalar reference types: ``ref<T>``, ``iref<T>``, ``weakref<T>``,
   ``funcref<sig>``, ``threadref``, ``stackref``, ``framecursorref``,
   ``irbuilderref`` and ``tagref64``. These types refer to "things" in the Mu
   micro VM. All such references are opaque in the sense that their
   representation is implementation dependent.

3. Composite types: ``struct<F1 F2 ...>``, ``array<T n>``, ``hybrid<F1 F2 ...
   V>`` and ``vector<T n>``. These types combine simpler types into more complex
   types.

4. The void type ``void``. It has only one use case: when used as the
   "referenced type" of references or pointers, it conveys the meaning of
   "reference/pointer to anything".

This is a complete list of Mu types. All values of Mu come from one of these
types.

Define Types and Function Signatures
====================================

Type definition
---------------

To define a type in Mu, you use the top-level type definition: ``.typedef``.

.. _types-examples:

.. code-block:: uir

    .typedef @i1     = int<1>
    .typedef @i8     = int<8>
    .typedef @i16    = int<16>
    .typedef @i32    = int<32>
    .typedef @i64    = int<64>
    .typedef @float  = float
    .typedef @double = double

    .typedef @ptri32 = uptr<@i32>
    .typedef @foo.fp = ufuncptr<@foo_sig>

    .typedef @refi32  = ref <@i32>
    .typedef @irefi64 = iref<@i64>
    .typedef @weakreffloat = weakref<@float>

    .funcsig @foo.sig = (@i32) -> (@i32)
    .typedef @foo.fr  = funcref<@foo_sig>

    .typedef @stackref  = stackref
    .typedef @threadref = threadref
    .typedef @stkref    = stackref
    .typedef @thrref    = threadref
    .typedef @fcref     = framecursorref
    .typedef @ibref     = irbuilderref

    .typedef @struct1 = struct<@i32 @i32 @i32>
    .typedef @struct2 = struct<@i64 @double>
    .typedef @array1  = array<@i32 10>
    .typedef @array2  = array<@i32 4096>
    .typedef @hybrid1 = hybrid<@i64 @i32>
    .typedef @hybrid2 = hybrid<@i8>
    .typedef @hybrid3 = hybrid<@i64 @i64 @i64 @float>
    .typedef @4xi32   = vector<@i32 4>

    .typedef @void = void

Every type defined in the Mu IR has a name, which is on the left side of the
equal sign. All characters in ``[a-zA-Z0-9_.]`` are legal. You can use the dot
``.`` arbitrarily in the name. So the dot in ``@foo.sig`` does not mean anything
special to Mu.

.. _type-constructor:

On the right side of the equal sign is the **type constructor**: it constructs a
type. Some type constructors take parameters while others do not.

*What are type constructors?*

If we imagine a Mu type as a Java or C++ object, then the type constructor
is like the constructor of such an object. ``int`` is just the abstract concept
of integer, but ``int<32>`` is a concrete 32-bit integer type.  Similarly
``ref<@i32>`` constructs a reference type to ``@i32``:

.. code-block:: uir

    .typedef @i32    = int<32>
    .typedef @refi32 = ref<@i32>

Some type constructors, such as ``float``, ``double``, ``threadref`` or
``void``, do not take any parameters. You can consider them as C++/Java
constructors with an empty parameter list. You may have written ``new Object()``
or ``new StringBuilder()`` before. Similarly you define a concrete instance of
``float`` type in this way:

.. code-block:: uir

    .typedef @float    = float
    .typedef @blahblah = float

, where the name ``@float`` or ``@blahblah`` are just names.

When types or function signatures are taken as argument, their names (such as
``@i32``, ``@float`` and ``@void``, not ``int<32>``, ``float`` or ``void``) are
used. So the following are not accepted by Holstein:

.. code-block:: uir

    .typedef @refi32  = ref<int<32>> // ERROR! int<32> must be defined separately.
    .typedef @refvoid = ref<void>    // ERROR! void must be defined separately.
    .typedef @bar.ref = funcref<(@i32) -> (@float)> // ERROR! The signature must be defined separately.

But these are right:

.. code-block:: uir

    .typedef @i32     = int<32>
    .typedef @refi32  = ref<@i32>  // Correct.

    .typedef @void    = void
    .typedef @refvoid = ref<@void> // Correct.

    .typedef @float   = float
    .funcsig @bar.sig = (@i32) -> (@float)
    .typedef @bar.ref = funcref<@bar.sig>   // Correct.

.. note::

    So why does Mu force all types to be "constructed" at the top level? Well,
    that's what Holstein accepts now.  There are `alternative text Mu IR parsers
    <https://gitlab.anu.edu.au/mu/mu-tool-compiler>`__ that accept in-line types
    such as ``ref<int<32>>``.

    Actually, productional Mu and client implementations will use the `IR
    building API
    <https://gitlab.anu.edu.au/mu/mu-spec/blob/master/irbuilder.rst>`__.  It
    will skip the text parsing phase completely.

    The reason why Holstein was designed like that was to let the text match the
    actual data structure of the IR.  In the IR building API, each type is a
    "node".  Types that have parameters (such as ``ref<T>``) refer to other
    nodes by their IDs.  Similarly, in the text form, such type constructors
    refer to other types by names.

    If you have used LLVM before, you may find that you can write types
    "directly", "inline", in the LLVM IR, such as:

    .. code-block:: llvm

        %c = add i32 %a, %b
        %f = fadd double %d, %e
        %g = load i32* %x

    But have a look at the C++ API of the LLVM:

    .. code-block:: cpp

        Type *i32 = Type::getInt32Ty(ctx);
        Type *i64 = IntegerType::get(ctx, 64);  // alternative method
        Type *floatTy  = Type::getFloatTy(ctx);
        Type *doubleTy = Type::getDoubleTy(ctx);
        Type *voidTy   = Type::getVoidTy(ctx);

        Type *blahblah = Type::getFloatTy(ctx);

        Type *ptri32 = Type::getInt32PtrTy(ctx);
        Type *ptri64 = PointerType::getUnqual(i64);

    .. ****** Comment: The grumpy Vim is not happy with the stars.

    In this API, the programmer still needs to refer to types by pointers to the
    types. So this API is more similar to having to define (or, at least, make
    pointers to) the types separately.

    On the other hand, there is only 19 types in the Mu type system, among which
    only 6 do not take arguments. Even if the client programmer has to define
    each and every types, all common types can be defined in about 20 lines as
    :ref:`above <types-examples>`, and his/her pain ends there.

Function signature definition
-----------------------------

A **function signature** defines the parameter types and the return types of a
function. It is defined by the ``.funcsig`` top-level definition:

.. code-block:: uir

    .typedef @i32     = int<32>
    .typedef @float   = float

    .funcsig @sig1    = (@i32) -> (@float)
    .funcsig @sig2    = (@i32 @i32 @i32) -> (@i32 @float)
    .funcsig @sig3    = () -> (@i32)
    .funcsig @sig4    = (@i32) -> ()
    .funcsig @sig5    = () -> ()

    .typedef @funcref1  = funcref <@sig1>
    .typedef @ufuncptr1 = ufuncptr<@sig1>

On the left side of ``=`` is the name of the signature. On the right side is the
function signature constructor. In Mu, a function takes 0 or more parameters and
return 0 or more values. It is written in the form ``(parameter types) ->
(return types)``.

A function signature is **not** a type. Unlike the C or C++ programming
language, there is no "function type" in Mu. In fact, in C, if an expression has
function type, it is implicitly converted to the pointer of that function. Mu
takes the explicit approach: there are two types that use function signatures:

- The ``funcref<sig>`` type refers to a Mu function which has signature ``sig``.

- The ``ufuncptr<sig>`` type is a pointer that points to a native function that
  has signature ``sig``.

When defining or declaring functions, such as:

.. code-block:: uir

    .funcdecl @foo <@sig1>

    .funcdef @bar VERSION %v1 <@sig2> {
        ...
        %rv = CALL <@sig1> @foo (...) // arguments omitted
        ...
    }

The names of the functions ``@foo`` and ``@bar`` has the ``funcref<@sig1>`` and
the ``funcref<@sig2>`` type, respectively, when used as a value.

Details
=======

This section will only discuss the most important types. For more details, you
can read the `Type System section
<https://gitlab.anu.edu.au/mu/mu-spec/blob/master/type-system.rst>`__ of the
specification.

Integer and FP types
--------------------
   
``int<n>`` is the **integer** type of ``n`` bits. Like LLVM, the ``int`` type is
fixed-length. For example, ``int<32>`` is the 32-bit integer type.

.. code-block:: uir

    .typedef @i32 = int<32>
    .typedef @i64 = int<64>

It is also signedness-neutral: whether an integer is signed or not depends on
the operation, not the type. Most instructions, such as ``ADD``, ``SUB``,
``MUL``, work correctly for both signed and unsigned integers. Some instructions
have signed and unsigned variants, such as ``SDIV``/``UDIV``,
``FPTOSI``/``FPTOUI``.

Like LLVM, ``int<1>`` is returned by most instructions that return Boolean
results, such as ``EQ`` and ``SLT``.

.. code-block:: uir

    .typedef @i1 = int<1>

``float`` and ``double`` are the IEEE 754 single and double-precision **floating
point** number types, respectively.

.. code-block:: uir

    .typedef @float  = float
    .typedef @double = double

Like LLVM but unlike some intermediate languages such as `C minus minus
<https://en.wikipedia.org/wiki/C-->`__, Mu does not use a single type (such as
"bits32") to hold both integers and FP numbers, because in modern machines
integers and FP numbers are usually held in different kinds of registers.

References to the memory
------------------------

``ref<T>`` is the **object reference** type. It refers to objects in the
garbage-collected Mu heap.

``iref<T>`` is the **internal reference** type. It refers to a *memory
location*, that is, a place in the Mu memory that can be loaded or stored. A
field of a heap object is a memory location.

.. attention::

    "Memory location" does not mean "address". Do not assume a Mu heap object or
    any other memory locations have addresses. This is very important in Mu.
    This will discussed in details in later chapters. The specification contains
    `some explanation
    <https://gitlab.anu.edu.au/mu/mu-spec/blob/master/memory.rst#basic-concepts>`__

Both ``ref`` and ``iref`` may be ``NULL``.

.. note::

    Sorry for the `billion-dollar mistake
    <https://en.wikipedia.org/wiki/Null_pointer#History>`__, but ``NULL`` is
    really easy to implement, and Mu is closer to the machine. The client, on
    the other hand, should implement a decent language and help the programmers
    prevent such mistakes.)

The ``<T>`` type parameter is the type of the heap object it refers to.

For ``ref<T>``, the ``T`` means it refers to a heap object of type ``T``. For
example, ``ref<@i32>`` refers to a heap object of ``@i32`` type, which we
previously defined as ``int<32>``:

.. code-block:: uir

    .typedef @refi32    = ref<@i32>
    .typedef @refdouble = ref<@double>

    .typedef @link = ref<@link>

In the last line, ``@link`` is recursively defined as ``ref<@link>``. It means
it refers to a heap object, whose entire content is an object reference to the
same type, or ``NULL``. It is very similar to the C definition: ``struct Link {
struct Link *next; }``. Mu does not need ``struct`` to construct recursive
types.

For ``iref<T>``, the ``T`` means it refers to a memory location of type ``T``.
So if you use the ``LOAD`` instruction on an ``iref<@i32>``, you get a value of
type ``@i32``. You can also ``STORE`` an ``@i64`` value to a memory location
referred by an ``iref<@i64>``.

.. code-block:: uir

    .typedef @irefi32   = iref<@i32>
    .typedef @irefi64   = iref<@i64>

References to Mu functions
--------------------------

``funcref<sig>`` is the **function reference** type. It refers to a Mu
function. Whenever you call a Mu function, you call it with its function
reference. ``sig`` is the function signature.

.. code-block:: uir

    .funcsig @sig1      = (@i32) -> (@float)
    .typedef @funcref1  = funcref <@sig1>

``funcref`` only refers to Mu functions. It cannot refer to C functions (that is
what ``ufuncptr`` is for).

Like other references, ``funcref`` can also be ``NULL`` (sorry).

Aggregate types
---------------

Among all aggregate types, ``hybrid`` is the only "variable-length" types. All
others are "fixed-length".

Fixed-length aggregate types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``struct<F1 F2 ...>`` is the **structure** type. Like the *struct* type in
C, it has many fields of types ``F1``, ``F2``, ...

.. code-block:: uir

    .typedef @struct1 = struct<@i32 @i32 @i32>
    .typedef @struct2 = struct<@i64 @double>

Structs may contain other structs, arrays or vectors, but cannot contain
themselves (otherwise it will be infinitely big). It must have at least one
field. But it may contain references so that you can allocate many structs in
the Mu heap, each refer to another object.

.. code-block:: uir

    .typedef @ListNode    = struct<@i64 @ListNodeRef>
    .typedef @ListNodeRef = ref<@ListNode>

``array<T n>`` is the **fixed-size array** type. ``T`` is the element type.
``n`` is an integer literal and it is part of the type. A particular
``array<T n>`` holds exactly ``n`` instances of ``T``. For example, ``array<@i32
10>`` contains exactly 10 ``@i32`` values:

.. code-block:: uir
    
    .typedef @array1  = array<@i32 10>
    .typedef @array2  = array<@i32 4096>

Like structs, arrays may contain other structs, arrays or vectors, but not
itself. It must have at least one element. Arrays of references are allowed.

``vector<T n>`` is the **vector** type. It is designed for single-instruction
multiple-data (SIMD) operations. Most modern desktop processors have SIMD
capabilities. Vectors are used in very different ways compared to arrays.
Vectors are usually small and are usually similar to the vector sizes supported
by the machine.

Even today, architectures still do not agree upon any particular vector sizes.
Mu only mandate the following three vector types to be implemented:

.. code-block:: uir
    
    .typedef @4xi32    = vector<@i32 4>
    .typedef @4xfloat  = vector<@float 4>
    .typedef @2xdouble = vector<@double 2>

The hybrid
~~~~~~~~~~

``hybrid<F1 F2 ... V>`` is a **hybrid** of a struct and an array. It starts
with a *fixed part*: ``F1``, ``F2``, ... which is like a struct. It is
followed by a *variable part*: an array of many elements of type ``V``.

.. code-block:: uir

    .typedef @hybrid1 = hybrid<@i64 @i32>
    .typedef @hybrid2 = hybrid<@i8>
    .typedef @hybrid3 = hybrid<@i64 @i64 @i64 @float>

In the above example, ``@hybrid1`` has one ``@i64`` field in its fixed part, and
many ``@i32`` elements in its variable part. ``@hybrid2`` has an empty fixed
part, and its variable parts are many ``@i8`` elements. ``@hybrid3`` has three
``@i64`` fields in its fixed part, and many ``@float`` elements in the variable
part.

``hybrid`` is *the only variable-size type* type in Mu whose size is determined
at allocation site rather than the type itself. A hybrid must be allocated by
special instructions, such as ``NEWHYBRID``, which takes not only the type but
also the length as its arguments.

.. code-block:: uir

    %length1 = .....
    %length2 = .....
    %r1 = NEWHYBRID <@hybrid1 @i64> %length1  // @i64 is the length of %length1
    %r2 = NEWHYBRID <@hybrid1 @i64> %length2  // @i64 is the length of %length2

In the above example, ``%r1`` and ``%r2`` refers to two different objects. Both
have type ``@hybrid1``, but the length of their variable parts are ``%length1``
and ``%length2``, respectively.

Since the length cannot be determined by the type itself, it cannot be embedded
in other aggregate types, not even other hybrids:

.. code-block:: uir

    .typedef @some_struct = struct<@i64 @hybrid1 @hybrid2> // ERROR! cannot embed hybrids

Hybrid is the counterpart of the C99 structs with "flexible array elements". In
C99, you can write something like:

.. code-block:: cpp

    struct hybrid1 { int64_t f1; int32_t v[]; };
    struct hybrid2 { int32_t v[]; };
    struct hybrid3 { int64_t f1, f2, f3; float v[]; };

    struct hybrid1 *p1 = malloc(sizeof(int64_t) + 1000*sizeof(int32_t));
    struct hybrid1 *p2 = malloc(sizeof(int64_t) + 2000*sizeof(int32_t));

Once malloc-ed with enough memory, C can access the dynamically allocated "tail"
elements.

The void type
-------------

``void`` means "anything", and can only be used as the target of references or
pointers. For example:

.. code-block:: uir

    .typedef @void = void
    .typedef @refvoid  = ref<@void>
    .typedef @irefvoid = iref<@void>
    .typedef @uptrvoid = uptr<@void>

``ref<@void>`` means the object reference can refer to any object.
``iref<@void>`` means the internal reference can refer to any memory location.
``uptr<@void>`` means it is... err... just a pointer, and has not been assigned
a type yet.

Mu does not have the concept of "inheritance", but there are some "prefix rules"
so that a reference may refer to some more complex objects than its ``<T>``
parameter. ``void`` is just the "simplest" type: no content at all.

You can allocate heap objects of the ``void`` type.

.. code-block:: uir

    %r = NEW <@void>

Such objects have no contents, but each allocated ``void`` object is different,
and compares equal (``EQ``) to only itself.

In Java, such use is like ``Object o1 = new Object();``. There are some corner
cases where such objects can be used as a "key" to identify something.

Other types
-----------

``stackref``, ``threadref`` and ``framecursorref`` refers to "special
things" in Mu: stacks, threads and frame cursors. You will need the first two to
start a Mu program, and need the third to perform stack introspection and
on-stack replacement.

``weakref<T>`` is the weak object reference type.

``tagref64`` is the **tagged reference type**. It uses some clever bit-magic to
reuse the NaN space of ``double`` to represent a tagged union of ``double``,
``int<52>`` and a struct of ``ref<void>`` and ``int<6>``.

``uptr<T>`` and ``ufuncptr<sig>`` are **untraced (raw) pointers**. They are
defined to be represented as integers of the pointer size, which is
implementation-specific. For example, on a 64-bit implementation, it is 64 bits.
But if you want to perform pointer arithmetic, you need to convert them to
integers first.

You are unlikely to use raw pointers unless your program interacts with native
programs (usually written in C). The garbage collector will not trace them: they
are treated just like integers.
  
If you worked with x86 before, you may ask: Wait! Pointer is not just the
address, but also its segment. Sorry, x86. But we see the trend is to move away
from segmented architecture (x86_64 moved away from segments, too). For embedded
systems that may have multiple address spaces, Mu is not designed for such
systems, but supporting such architectures is an open topic.

Bonus section
=============

.. note::

    These contents should be moved to other chapters in the future. But if you
    are interested and patient enough, you can keep reading.

In fact, an internal reference refers to a "**memory location**" (discussed
in later chapters) of type ``T``.  Memory location is a very important
concept in Mu. It is a location in the Mu memory that can hold a Mu value.
A field of an object is one kind of memory location. All memory accessing
operations, such as ``LOAD`` and ``STORE`` directly work on internal
references. This is different from JVM, where there are ``getfield`` and
``setfield`` instructions that work on object references.

If you worked with C before, it is the counterpart of the concept of
"object". (What? You say C does not have "objects" but C++ does? Go ahead
and read the `C specification
<http://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf>`__. In C,
"object" means "a region of data storage" and does not mean object-oriented
programming.) But the word "object" is used as a synonym of "heap object"
in Mu. To avoid ambiguity, we use the word "memory location" instead.

.. vim: tw=80
