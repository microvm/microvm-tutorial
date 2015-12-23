# -*- coding: utf-8 -*-
import re

from pygments.lexer import *
from pygments.token import *

__all__ = ['UirLexer']


class UirLexer(RegexLexer):
    name = 'Mu Intermediate Representation'
    aliases = ['uir']
    filenames = ['*.uir']
    mimetypes = ['text/x-uir']

    tokens = {
        'root': [
            (r'//.*?$', Comment.Single),
            (words(('.typedef .funcsig .const .global .funcdef .funcdecl .expose'
                ).split(), suffix=r'\b'), Keyword.Declaration),
            (words(('int float double ref iref weakref struct array hybrid void '
                'funcref threadref stackref framecursorref '
                'tagref64 vector uptr ufuncptr').split(), suffix=r'\b'), Keyword.Type),
            (words(('''ADD SUB MUL UDIV SDIV UREM SREM SHL LSHR ASHR AND OR XOR
                        FADD FSUB FMUL FDIV FREM
                        EQ NE ULT ULE UGT UGE SLT SLE SGT SGE
                        FTRUE FFALSE FORD FOEQ FONE FOLT FOLE FOGT FOGE
                        FUNO FUEQ FUNE FULT FULE FUGT FUGE
                        TRUNC ZEXT SEXT FPTRUNC FPEXT FPTOUI FPTOSI UITOFP SITOFP
                        BITCAST REFCAST PTRCAST
                        SELECT BRANCH BRANCH2 SWITCH CALL TAILCALL
                        RET THROW EXTRACTVALUE INSERTVALUE
                        EXTRACTELEMENT INSERTELEMENT SHUFFLEVECTOR
                        NEW NEWHYBRID ALLOCA ALLOCAHYBRID GETIREF GETFIELDIREF
                        GETELEMIREF SHIFTIREF GETVARPARTIREF
                        LOAD STORE CMPXCHG ATOMICRMW FENCE TRAP WATCHPOINT WPBRANCH
                        CCALL NEWTHREAD SWAPSTACK COMMINST
                ''').split(), suffix=r'\b'), Operator.Word),
            (words(('''NOT_ATOMIC RELAXED CONSUME ACQUIRE RELEASE ACQ_REL SEQ_CST
                        XCHG ADD SUB AND NAND OR XOR MIN MAX UMIN UMAX
                        bitsf bitsd VERSION EXC KEEPALIVE WEAK WPEXC PTR
                        RET_WITH KILL_OLD
                        PASS_VALUES THROW_EXC
                ''').split(), suffix=r'\b'), Keyword.Reserved),
            (r'([@][a-zA-Z0-9_\-.]+)\b', Name.Variable.Global),
            (r'([%][a-zA-Z0-9_\-.]+)\b', Name.Variable),
            (r'(([0-9]+\.[0-9]+(e[+-]?[0-9]+)?|nan|[+-]?inf)[fd])\b', Number.Float),
            (r'([+-]?(0[xX][0-9a-fA-F]+|0[0-7]*|[1-9][0-9]*))\b', Number.Integer),
            (r'NULL\b', Keyword.Constant),
            (r'([=<>\(\){}:;]|->)', Punctuation),
            (r'#[A-Z_]+\b', Literal),
            (r'\s+', Whitespace),
        ],
    }

