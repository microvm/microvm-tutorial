========================
Interacting With the µVM
========================

The client interacts with the µVM in two ways: the *µVM IR* and the *µVM-client
API*.

µVM Intermediate Representation
===============================

The code which µVM reads and executes is called the **µVM Intermediate
Representation**, or **µVM IR** for short.

Here is an example bundle in the text format.

.. code-block:: uir

    .typedef @i64       = int<64>
    .typedef @double    = double
    .typedef @void      = void
    .typedef @just_another_void = void
    .typedef @still_void = void
    .typedef @refvoid   = ref<@void>

    .const @i64_0 <@i64>  = 0
    .const @answer <@i64> = 42

    .typedef @some_global_data_t = struct <@i64 @double @refvoid>
    .global @some_global_data <@some_global_data_t>

    .typedef @Node = struct<@i64 @NodeRef>
    .typedef @NodeRef = ref<@Node>

    .funcsig @BinaryFunc = @i64 (@i64 @i64)

    .funcdecl @square_sum <@BinaryFunc>

    .funcdef @gcd VERSION @gcd_v1 <@BinaryFunc> (%a0 %b0) {
        %entry:
            BRANCH %head

        %head:
            %a = PHI <@i64> { %entry: %a0; %body: %b; }
            %b = PHI <@i64> { %entry: %b0; %body: %b1; }

            %z = EQ <@i64> %b @i64_0
            BRANCH2 %z %exit %body

        %body:
            %b1 = SREM <@i64> %a %b
            BRANCH %head

        %exit:
            RET <@i64> %a
    }

    .const @I64_18 <@i64> = 18
    .const @I64_12 <@i64> = 12

    .funcsig @main_sig = @void ()
    .funcdef @main VERSION @main_v1 <@main_sig> () {
        %entry:
            %result = CALL <@BinaryFunc> @gcd (@I64_18 @I64_12)

            %the_trap = TRAP <@void> KEEPALIVE(%result)

            COMMINST @uvm.thread_exit
    }

A bundle has many top-level definitions.

Top-level definitions begin with a word with a dot ``.``. For example,
``.typedef @i64 = int<64>`` defines a type: 64-bit integer, and binds a name
``@i64`` to that type. Similarly, ``.typedef @void = void`` binds the name
``@void`` to the void type.

    You can even bind more than one names to the "same" type. When referred to
    later, ``@void``, ``@just_another_void``, ``@still_void`` will not have any
    noticeable difference from the client's point of view. (Of course from the
    µVM implementer's point of view they are somewhat different)

Similarly, ``.const``, ``.global``, ``.funcsig``, ``.funcdef``, ``.funcdecl``
define constants, global cells, function signatures, functions and function
versions, and also give them names. Inside a function version (e.g. ``@gcd``
VERSION ``@gcd_v1``), parameters (``%a0``, ``%b0``) basic blocks (``%entry``,
``%head``, ...) and instructions (``%a``, ``%b``, ...) also have names.

    You may have noticed the term *function version*. Functions in the µVM have
    versions. They will be introduced later. For now, just remember that every
    "function body" is a version of a function; every ``.funcdef`` must have a
    body and, thus, defines a new version of a function.

In the µVM IR, every **named entity** except instructions must have a name.  In
the µVM, *types*, *function signatures*, *constants*, *global cells*,
*functions*, *function versions*, *parameters*, *basic blocks* and
*instructions* are named entities.

There are **global names** (start with ``@``) and **local names** (start with
``%``). Local names are simply for the convenience of writing. It is exactly
equivalent to ``@func_ver_name.local_name`` where ``func_ver_name`` is the name
of the function version (not including the ``@``) and ``local_name`` is the
local name (not including the ``%``). For example, the name ``%body`` in
``@gcd_v1`` is equivalent to ``@gcd_v1.body``, and ``%b1`` is equivalent to
``@gcd_v1.b1``.

Inside a function version, there are many basic blocks. The first block is the
"entry block" and is conventionally named ``%entry``. Each basic block has many
instructions.

    If you worked with LLVM before, you may find it very familiar. Indeed the
    µVM is inspired by the LLVM. It also uses the SSA form.

Each instruction performs a certain computation. The name of an instruction can
be used to refer to the instruction itself, or the result produced by that
instruction. For this reason, it is also called a variable.

There is one instruction that needs special attention at this moment: the
``TRAP`` instruction. From time to time, the program written in the µVM IR will
need to handle events which the µVM cannot handle alone. The ``TRAP`` is like a
special jump. It transfers the control from the µVM IR program to the client. A
registered *trap handler* in the client will handle such an event.

This is so far you need to know about the µVM IR.

    Exercise: Load the bundle above into a µVM instance.

µVM-client Interface
====================

.. vim: tw=80
