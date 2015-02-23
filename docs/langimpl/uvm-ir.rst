========================
Interacting With the µVM
========================

µVM Intermediate Representation
===============================

The code which µVM reads and executes is called the **µVM Intermediate
Representation**, or **µVM IR** for short.

.. code-block:: uir

    .typedef @i64 = int<64>
    .typedef @double = double
    .typedef @void = void
    .typedef @refvoid = ref<@void>

    .const @i64_0 <@i64> = 0
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

.. vim: tw=80
