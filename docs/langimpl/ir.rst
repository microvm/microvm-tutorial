===============================
Mu Intermediate Representation
===============================

The client generates code in the format of **Mu Intermediate Representation**,
or **Mu IR** for short. The IR is the language in which programs are represented
in the Mu micro VM. The Mu IR is defined by the `Mu IR chapter
<https://gitlab.anu.edu.au/mu/mu-spec/blob/master/ir.rst>`__ of the Mu
specification.

The structure of the Mu IR is an AST.  Mu bundle has a text form for human
readability.  A bundle can also be built using the `IR building API
<https://gitlab.anu.edu.au/mu/mu-spec/blob/master/irbuilder.rst>`__ which calls
into Mu to build an AST inside Mu.  The IR building API is designed for
productional setting.  This tutorial will use the text-form API.

Bundle
======

The client submits one **bundle** (a piece of Mu IR code) at a time to the Mu
micro VM.

.. code-block:: scala

    ctx.loadBundle("""
        // insert your bundle here
    """)


A bundle defines many *types*, *function signatures*, *constants*, *global cell*
and *functions*. The client may submit multiple bundles one after another.

After submitting, Mu knows about those things. Types can be used, global cells
are allocated, and functions are callable.

A bundle looks like this:

.. code-block:: uir

    // Type
    .typedef @i64 = int<64>

    // Function signature
    .funcsig @i_to_i = (@i64) -> (@i64)

    // Constant
    .const @I64_1 <@i64> = 1
    .const @I64_2 <@i64> = 2

    // Global cell
    .global @g_foo <@i64>

    // Function declaration (no body)
    .funcdecl @factorial <@i_to_i>

    // Function definition (with body)
    .funcdef @fibonacci VERSION %v1 <@i_to_i> {
        %entry(<@i64> %n):                          // Basic block
            %lt = SLT <@i64> %n @I64_2                  // Instructions
            BRANCH2 %lt %small(%n) %big(%n)             // Instructions

        %small(<@i64> %n):                          // Basic block
            RET %n                                      // Interaction

        %big(<@i64> %n):                            // Basic block
            %nm1 = SUB <@i64> %n @I64_1                 // Instruction
            %nm2 = SUB <@i64> %n @I64_2                 // Instruction
            %v1  = CALL <@i_to_i> @fibonacci (%nm1)     // Instruction
            %v2  = CALL <@i_to_i> @fibonacci (%nm2)     // Instruction
            %rv  = ADD <@i64> %v1 %v2                   // Instruction
            RET %rv                                     // Instruction
    }

If you have used LLVM before, the Mu IR is the counterpart of LLVM modules.

Names
=====

You may have noticed that there are names for almost all entities. In the Mu IR,
there are two kinds of names: global names and local names. Global names start
with ``@`` and local names start with ``%``. The allowed characters in names are
``[a-zA-Z0-9_.]``.

In fact, local names are just syntax sugars of some global names, that is,
anything that has a name has a global name. This will be discussed later.

At this moment, you only need to know what a bundle may contain. Their details
will be discussed in the following chapters.

.. vim: tw=80
