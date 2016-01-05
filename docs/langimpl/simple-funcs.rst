================
Simple Functions
================

The constant and function syntax is defined in the `Intermediate Representation
<https://github.com/microvm/microvm-spec/blob/master/uvm-ir.rest>`__ chapter of
the specification.

The Mu IR uses a variant of the `static single assignment (SSA)
<https://en.wikipedia.org/wiki/Static_single_assignment_form>`__ or `static
single information (SSI)
<http://publications.csail.mit.edu/lcs/pubs/pdf/MIT-LCS-TR-801.pdf>`__ form. Mu
IR has control flow graphs (CFG), each has many basic blocks, each then has many
parameters and instructions. The main difference is that basic blocks take
parameters, which are the counterpart of the PHI-nodes in SSA. At the end of a
basic block, if it branches to another basic block, it must also specify the
arguments to the destination, which are the counterpart of the SIGMA-nodes in
SSI. There is no explicit PHI- or SIGMA-node. Instructions can only use global
variables, the parameters of the basic block it is in, or the variables
evaluated before that instruction in the same basic block. In other words, each
basic block is a local scope and is like a single-exit "straight-line" function.

SSA Variable
============

In the Mu IR, as in SSA, a variable is defined in exactly one place and never
redefined. For this reason, we still call them **SSA variables** since they are
only assigned in one place.

In the Mu IR, variables are referred to by names, such as ``@foo`` or ``%bar``.

Variables can be global or local. Global SSA variables are globally valid and
never change. (Sorry but we still call them "variables".) Local SSA variables
are only valid within a basic block and gets a value every time it is evaluated.
Oh, did I say variables are defined in one *place*? Yes, they are, but this does
not prevent them from being assigned multiple *times*. That is what "static"
single assignment means.

Constant Definitions
====================

**Constant definitions**, i.e. ``.const``, are a kind of top-level definition.
They construct values using literals.

.. code-block:: uir

    .typedef @i8     = int<8>
    .typedef @i16    = int<16>
    .typedef @i32    = int<32>
    .typedef @i64    = int<64>
    .typedef @float  = float
    .typedef @double = double
    .typedef @refi64 = ref<@i64>

    .const @I8_10  <@i8>  = 10
    .const @I16_10 <@i16> = 10
    .const @I32_10 <@i32> = 10
    .const @I64_10 <@i64> = 10
    .const @MAGIC_NUMBER1 <@i64> = 0x123456789abcdef0
    .const @MAGIC_NUMBER2 <@i64> = 0xfedcba9876543210
    .const @MAGIC_NUMBER3 <@i64> = -0x8000000000000000

    .const @F_PI  <@float>  = 3.14f
    .const @D_2PI <@double> = 6.28d

    .const @MY_CONSTANT_REF <@refi64> = NULL

On the left side of ``=``, there are the name of the constant (such as
``@I8_10``) and its type (such as ``@i8``). On the right side it is, as you can
guess, the **constant constructor**.

To construct an integer, you can write it in the decimal form or the hexadecimal
form (add ``0x`` before). It may also have a sign. Since integers themselves in
Mu do not have signs, the integer literal is just used to encode the bit
pattern. Mu uses the 2's complement representation for negative numbers, so
``0xffffffff`` and ``-1`` are the same if both are 32-bit.

To construct a floating point number, you can write it in the decimal form, with
a decimal point (that is, 1.0, not 1), and append an ``f`` for float or a ``d``
for double. ``nanf``, ``+inff`` and ``-inff`` will construct NaN, positive
infinity and negative infinity of the ``float`` type. Replace the last ``f``
with ``d`` and it will be the ``double`` type.

.. code-block:: uir

    .const @F_NAN  <@float> = nanf   // Mu will interpret it as an arbitrary NaN
    .const @F_PINF <@float> = +inff  // positive infinity
    .const @F_NINF <@float> = -inff  // negative infinity

If you are an FP number wizard, you can also explicitly specify the bit layout
of an FP constant:

.. code-block:: uir

    .const @D_1    <@double> = bitsd(0x3ff0000000000000)   // +1.0
    .const @D_2    <@double> = bitsd(0x400c000000000000)   // +3.5
    .const @D_PINF <@double> = bitsd(0x7ff0000000000000)   // +inf
    .const @D_NAN  <@double> = bitsd(0x7ff0000000000001)   // nan (one possible encoding)

You can define constants of general reference types (``ref``, ``iref``,
``funcref``, ``threadref``, ``stackref`` and ``framecursorref``), too. But
the only possible constant value is ``NULL``.

.. code-block:: uir

    .typedef @refi64  = ref<@i64>
    .typedef @irefi64 = iref<@i64>
    .funcsig @foo.sig = () -> ()
    .typedef @foo.fr  = funcref<@foo.sig>
    .typedef @tr      = threadref
    .typedef @sr      = stackref
    .typedef @fcr     = framecursorref

    .const @NULLREF  <@refi64>  = NULL
    .const @NULLIREF <@irefi64> = NULL
    .const @NULLFR   <@foo.fr>  = NULL
    .const @NULLTR   <@tr>      = NULL
    .const @NULLSR   <@sr>      = NULL
    .const @NULLFCR  <@fcr>     = NULL

That is, you cannot define a constant reference to any heap object.

.. note::

    Why there is no constant references to objects?
    
    First of all, constants, as the name suggests, never change. If a constant
    refers to an object, the object is immortal! But the reason why we use the
    heap is to use GC, which eventually recycles the object.

    Secondly, from the implementation's point of view, the advantage of using
    constants is that they can exist as immediate values in machine
    instructions, or be created by some machine code idioms (e.g. ``xor rax,
    rax`` makes rax 0, and the instruction decoder in modern processors (since
    IvyBridge) can eliminate such "idioms" in the front end), rather than being
    stored in the memory and loaded when needed (memory is slow nowadays
    compared to 20 years ago). But if the type is object reference, perhaps the
    only feasible way to implement such constant is to store it in the memory so
    that copying GC can update it when the referenced object is moved.
    Non-copying GC sucks, because the VM will eventually die of heap
    fragmentation. (`R.I.P. lighttpd.
    <http://redmine.lighttpd.net/issues/758>`__ You know, C programmers are
    responsible for memory management. If C's malloc cannot manage the memory
    well and kills long-running servers, we should use a VM with copying GC,
    instead. If usual VMs perform too bad, that's why we build the Mu micro VM.)
    But if the GC ends up modifying the machine code to fix the reference, it
    will be too painful.

    If we really need some permanent global memory space, Mu has another
    top-level definition: global cells, i.e. ``.global`` (it will be discussed
    in details when we talk about memory access). Global cells are memory
    locations: they are mutable. They can be loaded and stored, and they are
    permanent. Just store an object reference in a global cell and it has all
    the benefits of constant references.

    For other references, constant function reference is unnecessary because the
    name of the function is already a constant function reference. Stacks are
    similar to heap objects. Threads and frame cursors have their own
    lifecycles, so you can't possibly create such constants that remain valid.

However, pointers are not references. They are just integers and can be
constructed as integers.

.. code-block:: uir

    .typedef @i64    = int<64>
    .typedef @ptri64 = uptr<@i64>

    .const @MY_POINTER <@ptri64> = 0x123456789000

    .funcsig @bar.sig = () -> ()
    .typedef @bar.fp  = ufuncptr<@bar.sig>

    // The address can be looked up by dlsym.
    .const @MY_FUNCTION_POINTER <@bar.fp> = 0x7fff00001230

Mu support constants of non-hybrid composite types, too. A composite constant is
constructed by referring to other constants. Please put as many fields/elements
as there should be.

.. code-block:: uir

    .typedef @i32     = int<32>
    .typedef @struct1 = struct<@i32 @i32 @i32>
    .typedef @array1  = array<@i32 2>
    .typedef @vector1 = vector<@i32 4>

    .const @I32_1 <@i32> = 1
    .const @I32_2 <@i32> = 2
    .const @I32_3 <@i32> = 3
    .const @I32_4 <@i32> = 4
    .const @S1    <@struct1> = { @I32_1 @I32_2 @I32_3 }
    .const @A1    <@array1>  = { @I32_1 @I32_2 }
    .const @V1    <@vector1> = { @I32_1 @I32_2 @I32_3 @I32_4 }

    .typedef @struct2 = struct<@struct1 @i64>

    .const @S2    <@struct2> = { @S1 @I32_4 }   // correct

    .const @WRONG <@struct2> = { {@I32_1 @I32_2 @I32_3} @I32_4 }   // ERROR: cannot nest braces. Define separately

But it is *not recommended to use constants of composite types, unless they are
small*. Mu may not be able to allocate big values into registers, in which case
it may perform stupid copying. The micro VM may not be smart enough to do too
much optimisation.

Function definition
===================

TODO

.. vim: tw=80
