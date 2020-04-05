
# ctags and vim

When you use vi and ctags in combination, you can place the cursor on an identifier and hit `Ctrl-]` to hop to its definition.

Here is the command to create a ctags file, recursively processing any source code files found in the current directory and its subdirectories:

    ctags -R -f .tags .

This is the snippet of my `.vimrc` file that loads the various ctags files that I have created for ledger C code:

    set tags+=/home/projects/ledger-app-btc/src/.tags
    set tags+=/home/projects/ledger-app-btc/include/.tags
    set tags+=/home/projects/nanos-secure-sdk/src/.tags
    set tags+=/home/projects/nanos-secure-sdk/include/.tags

This is the command to generate a ctags file for Python scripts:

    ctags -R --languages=python -f .tags

Here is the snippet of my `.vimrc` file that loads all of the ctags files relating to ledger Python scripts:

    set tags+=/home/projects/blue-loader-python/ledgerblue/.tags
    "set tags+=/home/projects/btchip-python/btchip/.tags
    set tags+=/home/projects/HWI/hwilib/.tags

The ctags file for HWI also includes tags for HWI's copy of btchip-python, found in directory `HWI/hwilib/devices/btchip`.

