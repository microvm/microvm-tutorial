# -*- coding: utf-8 -*-
import re

from pygments.lexer import *
from pygments.token import *

__all__ = ['UirLexer']


class UirLexer(RegexLexer):
    name = 'Mirovm Intermediate Representation'
    aliases = ['uir']
    filenames = ['*.uir']
    mimetypes = ['text/x-uir']

    tokens = {
        'root': [
            (r'//.*?$', Comment.Singleline),
            (words(('.typedef .funcsig .const .global .funcdef .funcdecl').split(), suffix=r'\b'), Keyword),
            (words(('int float double ref iref weakref struct array hybrid void func '
                'thread stack tagref64 vector').split(), suffix=r'\b'), Keyword.Type),
            (words(('''ADD SUB MUL UDIV SDIV UREM SREM SHL LSHR ASHR AND OR XOR
                        FADD FSUB FMUL FDIV FREM
                        EQ NE ULT ULE UGT UGE SLT SLE SGT SGE
                        FTRUE FFALSE FORD FOEQ FONE FOLT FOLE FOGT FOGE
                        FUNO FUEQ FUNE FULT FULE FUGT FUGE
                        TRUNC ZEXT SEXT FPTRUNC FPEXT FPTOUI FPTOSI UITOFP SITOFP
                        BITCAST REFCAST
                        SELECT BRANCH BRANCH2 SWITCH PHI CALL TAILCALL
                        RET RETVOID THROW LANDINGPAD EXTRACTVALUE INSERTVALUE
                        EXTRACTELEMENT INSERTELEMENT SHUFFLEVECTOR
                        NEW NEWHYBRID ALLOCA ALLOCAHYBRID GETIREF GETFIELDIREF
                        GETELEMIREF SHIFTIREF GETFIXEDPARTIREF GETVARPARTIREF
                        LOAD STORE CMPXCHG ATOMICRMW FENCE TRAP WATCHPOINT
                        CCALL NEWSTACK SWAPSTACK COMMINST
                        NOT_ATOMIC RELAXED CONSUME ACQUIRE CONSUME 
                        RELEASE ACQ_REL SEQ_CST
                        XCHG ADD SUB AND NAND OR XOR MIN MAX UMIN UMAX
                        DEFAULT
                        bitsf bitsd VEC VERSION EXC KEEPALIVE WEAK WPEXC
                        RET_WITH KILL_OLD
                        PASS_VALUE PASS_VOID THROW_EXC
                ''').split(), suffix=r'\b'), Keyword),
            (r'([@%][a-zA-Z0-9_\-.]+)\b', Name),
            (r'(([0-9]+\.[0-9]+(e[+-]?[0-9]+)?|nan|[+-]?inf)[fd])\b', Literal),
            (r'([+-]?(0[xX][0-9a-fA-F]+|0[0-7]*|[1-9][0-9]*))\b', Literal),
            ("NULL", Literal),
            (r'([=<>\(\){}:;])', Punctuation),
            (r'\s+', Whitespace),
        ],
    }

