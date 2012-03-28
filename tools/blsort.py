#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Build log sorter.

Author: Ed Bartosh <eduard.bartosh@intel.com>
Licence: GPLv2
"""

"""
Sorts the build log to make it possible to compare it to another build log. The
idea is to identify independend blocks of text first and then sort these
blocks. Blocks can be as follows.

1. All consequitive lines starting with the same file prefix belong to one
block, e.g.:
driver.c:355: warning: unused variable 'a'
driver.c:400: warning: no prototupe for function 'xxx'

2. GCC 'In file included from' blocks look like this:

In file included from include/linux/kernel.h:17:0,
                 from include/linux/sched.h:55,
                 from arch/arm/kernel/asm-offsets.c:13
include/linux/bitops.h: In function 'hweight_long':
include/linux/bitops.h:55:26: warning: signed and unsigned type in conditional expression [-Wsign-compare]

or

In file included from arch/x86/include/asm/uaccess.h:570:0,
                from include/linux/uaccess.h:5,
                from include/linux/highmem.h:7,
                from include/linux/pagemap.h:10,
                from fs/binfmt_misc.c:26:
In function ‘copy_from_user’,
    inlined from ‘parse_command.part.0’ at fs/binfmt_misc.c:422:20:
arch/x86/include/asm/uaccess_32.h:211:26: warning: call to ‘copy_from_user_overflow’ declared with attribute warning: copy_from_user() buffer size is not provably correct [enabled by default]

3. Any other line comprises an independent block
"""

import sys
import os
import re

def gen_blocks(stream):
    """Parses input stream. Yields found blocks."""

    btype = ""
    prefix = ""
    block = []
    for line in stream:
        # 'In file inculded' block
        if re.match("^In file included from .+", line):
            yield block
            btype = "ifi"
            prefix = ""
            block = [line]
        elif btype == "ifi" and re.match('^\s+', line):
            block.append(line)
        # filename prefixed block
        elif btype == "prefix" and line.startswith(prefix + ':'):
            block.append(line)
        elif re.match("^[^\s]+/[^\s]+:", line):
            yield block
            prefix = line.split(':')[0]
            btype = "prefix"
            block = [line]
        # the rest
        else:
            yield block
            btype = "plain"
            prefix = ""
            block = [line]

    yield block

def main(argv):
    """Script entry point."""

    infile = sys.stdin
    outfile = sys.stdout
    if len(argv) > 1:
        infile = open(argv[1])
    if len(argv) > 2:
        outfile = open(argv[2], "w")

    for block in sorted(gen_blocks(infile)):
        outfile.writelines(block)

    outfile.close()
    infile.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print "Usage: %s [<input log file>] [<sorted log file>]" % \
              os.path.basename(sys.argv[0])
        sys.exit(0)
    sys.exit(main(sys.argv))

# vim: ts=4 et sw=4 sts=4 ai sta:
