===========
Type System
===========

Like many programming languages, Mu also has a type system.

The type system is low level. There is no object-oriented programming concepts,
such as class, inheritance, polymorphism. There is no high-level concepts such
as strings, either. The language implementer is responsible to implement these
high-level concepts.

But the Mu type system is also not too low level. Notably, unlike C, C++ or
LLVM, the Mu type system still has object reference types in it, and the garbage
collector is fully aware of the presence of them. The main idea is, as long as
you use the Mu type system, and refer to heap objects using references, you can
forget about garbage collection details, such as stack maps, GC-safe points, and
read/write barriers.

Types
=====

Some of the types (actually :ref:`type constructors <type-constructor>`,
explained later) contain angular brackets. These are parameters to these types
which may be integer literals, other types or function signatures.

The types in the Mu type system can be put into several categories:

1. Scalar value types: ``int<n>``, ``float``, ``double``, ``uptr<T>`` and
   ``ufuncptr<sig>``. These types represent plain values.

2. Scalar reference types: ``ref<T>``, ``iref<T>``, ``weakref<T>``,
   ``funcref<sig>``, ``threadref``, ``stackref``, ``framecursorref`` and
   ``tagref64``. These types refer to "things" in the Mu micro VM. All such
   references are opaque in the sense that their representation is
   implementation dependent.

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

    .typedef @struct1 = struct<@i32 @i32 @i32>
    .typedef @struct2 = struct<@i64 @double>
    .typedef @array1  = array<@i32 10>
    .typedef @array2  = array<@i32 4096>
    .typedef @hybrid1 = hybrid<@i64 @i32>
    .typedef @hybrid2 = hybrid<@i32>
    .typedef @hybrid3 = hybrid<@i64 @i64 @i64 @i32>
    .typedef @4xi32   = vector<@i32 4>

    .typedef @void = void

Every type defined in the Mu IR has a name, which is on the left side of the
equal sign. All characters in ``[a-zA-Z0-9_.]`` are legal. You can use the dot
``.`` arbitrarily in the name. So the dot in ``@foo.sig`` does not mean anything
special to Mu.

.. _type-constructor:

On the right side of the equal sign is the **type constructor**: it constructs a
type. Some type constructor take parameters while others do not.

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
used. So the following is **wrong**:

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

    So why does Mu force all types to be "constructed" at the top level? For
    consistency. This greatly simplifies the syntax of the Mu IR and the amount
    of work the micro VM needs to do.

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

    On the other hand, there is only 18 types in the Mu type system, among which
    only 6 do not take arguments. Even if the client programmer has to define
    each and every types, all common types can be defined in about 20 lines as
    :ref:`above <types-examples>`, and his/her pain ends there.

    The Mu micro VM team is considering allowing the client to construct and
    load the Mu IR in language-specific and implementation-specific ways. In
    that case, the API would be more similar to the LLVM C++ API, which is even
    less likely to allow the "inline" syntax.

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
   
- ``int<n>`` is the **integer** type of ``n`` bits. Like LLVM, the ``int``
  type is fixed-length. For example, ``int<32>`` is the 32-bit integer type.
  It is also signedness-neutral: whether an integer is signed or not depends
  on the operation, not the type. Most instructions, such as ``ADD``,
  ``SUB``, ``MUL`` work correctly for both signed and unsigned integers. Some
  instructions have signed and unsigned variants, such as ``SDIV``/``UDIV``,
  ``FPTOSI``/``FPTOUI``. Like LLVM, ``int<1>`` is returned by most
  instructions that return Boolean results, such as ``EQ`` and ``SLT``.

- ``float`` and ``double`` are the IEEE 754 single and double-precision
  **floating point** number types, respectively.

- ``uptr<T>`` and ``ufuncptr<sig>`` are **untraced (raw) pointers**. These
  types are designed to interoperate with native programs (usually written in
  C) and they are defined to be represented as integers of the pointer size
  (but if you want to do arithmetic operations, you need to convert them to
  integers first, which is usually a no-op). The actual pointer size is
  implementation-specific. The garbage collector will not trace them: they
  are treated just like integers.
  
Like LLVM but unlike some intermediate languages such as `C minus minus
<https://en.wikipedia.org/wiki/C-->`__, Mu does not use a single type (such
as "bits32") to hold both integers and FP numbers, because in modern machines
integers and FP numbers are usually held in different kinds of registers.

If you worked with x86 before, you may ask: Wait! Pointer is not just the
address, but also its segment. Sorry, x86. But we see the trend is to move
away from segmented architecture (x86_64 moved away from segments, too). For
embedded systems that may have multiple address spaces, Mu is not designed
for such systems, but supporting such architectures is an open topic.


- ``ref<T>`` is the **object reference** type. It refers to objects in the
  garbage-collected Mu heap. It can also have the ``NULL`` value. (Sorry for
  the `billion-dollar mistake
  <https://en.wikipedia.org/wiki/Null_pointer#History>`__, but ``NULL`` is
  really easy to implement, and Mu is closer to the machine. The client, on
  the other hand, should implement a decent language and help the programmers
  prevent such mistakes.)

  The ``<T>`` type parameter is the type of the heap object it refers to. An
  "object" (a.k.a. a "heap object") is just some memory allocated in the heap
  and is subject to GC.  Although Mu does not have the concept of
  "inheritance", it has its own "prefix rule" (discussed in later chapters)
  so that a reference may refer to some objects more complex than the type
  parameter.

- ``iref<T>`` is the **internal reference** type. It may refer to a field of
  a heap object.
  
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

- ``weakref<T>`` is the weak object reference type. It will be discussed in
  later chapters.

- ``funcref<sig>`` is the **function reference** type. It refers to a Mu
  function. Whenever you call a Mu function, you call it with its function
  reference. ``sig`` is the function signature.

- ``stackref``, ``threadref`` and ``framecursorref`` refers to "special
  things" in Mu: stacks, threads and frame cursors.

- ``struct<F1 F2 ...>`` is the **structure** type. Like the *struct* type in
  C, it has many fields of types ``F1``, ``F2``, ...

- ``array<T n>`` is the **fixed-size array** type. ``T`` is the element type.
  ``n`` is an integer literal and it is part of the type. A particular
  ``array<T n>`` holds exactly ``n`` instances of ``T``.

- ``hybrid<F1 F2 ... V>`` is a **hybrid** of a struct and an array. It starts
  with a fixed part: ``F1``, ``F2``, ... which is like a struct. It is
  followed by a variable part: an array of many elements of type ``V``.

  ``hybrid`` is *the only type in Mu whose size is determined at allocation
  site rather than the type itself*. A hybrid must be allocated by special
  instructions, such as ``NEWHYBRID``, which takes not only the type but also
  the length as its arguments.



.. vim: tw=80
