#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Build log sorter.

Author: Ed Bartosh <eduard.bartosh@intel.com>
Licence: GPLv2
"""

# Sorts the build log to make it possible to compare it to another build log.
# The idea is to identify independend blocks of text first and then sort these
# blocks. Blocks can be as follows.
#
# 1. All consequitive lines starting with the same file prefix belong to one
# block, e.g.:
# driver.c:355: warning: unused variable 'a'
# driver.c:400: warning: no prototupe for function 'xxx'
#
# 2. GCC 'In file included from' blocks look like this:
#
# In file included from include/linux/kernel.h:17:0,
#                  from include/linux/sched.h:55,
#                  from arch/arm/kernel/asm-offsets.c:13
# include/linux/bitops.h: In function 'hweight_long':
# include/linux/bitops.h:55:26: warning: signed and unsigned type in expression
#
# or
#
# In file included from arch/x86/include/asm/uaccess.h:570:0,
#                 from include/linux/uaccess.h:5,
#                 from include/linux/highmem.h:7,
#                 from include/linux/pagemap.h:10,
#                 from fs/binfmt_misc.c:26:
# In function ‘copy_from_user’,
#     inlined from ‘parse_command.part.0’ at fs/binfmt_misc.c:422:20:
# arch/x86/include/asm/uaccess_32.h:211:26: warning: call to ‘copy_from_user’
#
# 3. Any other line comprises an independent block

import sys
import os
import re

def gen_blocks(stream):
    """Parses input stream. Yields found blocks."""

    prefix = ""
    block = []
    for line in stream:
        if re.match("^[^\s]+/[^\s]+:", line):
            new_prefix = line.split(':')[0]
        else:
            new_prefix = ""

        if re.match("^In file included from .+", line):
            yield block
            block = []
        elif prefix != "" and new_prefix != prefix:
            yield block
            block = []
        prefix = new_prefix
        block.append(line)

    yield block


def iter_both(iter1, iter2):
    """Iter two iterators. Return next not equal values from them until
       both are exhausted.
    """
    def get_next(iterator):
        """Get next item from the iterator. Return none
           if there are not items anymore.
        """
        try:
            return iterator.next()
        except StopIteration:
            return None

    while True:
        elem1, elem2 = get_next(iter1), get_next(iter2)

        if elem1 == None and elem2 == None:
            break
        if elem1 == elem2:
            continue
        yield elem1, elem2


def main(argv):
    """Script entry point."""

    infile1, infile2 = open(argv[1]), open(argv[2])
    outfile = sys.stdout
    if len(argv) > 3:
        outfile = open(argv[3], "w")

    with open(argv[1]) as infile1, \
         open(argv[2]) as infile2:

        result = {}
        for blk1, blk2 in iter_both(gen_blocks(infile1), gen_blocks(infile2)):
            for block, sign in [(tuple(blk1), "-"), (tuple(blk2), "+")]:
                if block:
                    if block in result:
                        del result[block]
                    else:
                        result[block] = sign

        result = sorted(result.items())
        if result:
            print "---", argv[1]
            print "+++", argv[2]
            for block, sign in result:
                print "@@ @@"
                for line in block:
                    print "%s%s" % (sign, line),

    outfile.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print "Usage: %s <input log 1> <input log 2> [<diff file>]" % \
              os.path.basename(sys.argv[0])
        sys.exit(0)
    sys.exit(main(sys.argv))

# vim: ts=4 et sw=4 sts=4 ai sta:
