# How-to guides

## How to define a positional argument

This is a python positional argument:

    @cli
    def mycommand(param):
        pass

This command should be used like this:

    mycommand myarg


## How to define an optional argument

Use a python keyword argument:

    @cli
    def mycommand(username=None):
        if not username:
            # prompt

This command can now be used like this to pass a given username:

    mycommand --username mike


## How to define a boolean optional argument

Simply use a python boolean keyword argument:

    @cli
    def mycommand(verbose=False):
        # pass

This command can now be used like this to make it verbose:

    mycommand --verbose


## How to use annotations

You can use annotation to specify the arguments types, for example:

    @cli
    def mycommand(param: int):
        print("Param is", param)

Annotations allow a lot of more subtle uses, here is how to receive a `Path`
instance for a `filepath` argument:

    import sys
    from pathlib import Path

    @cli
    def mycommand(path: Path):
        if not path.exists():
            sys.exit(f'Path {path} does not exist. Aborting')


### How to override the command name

You may want to override the command name, maybe because your are
using a python reserved keyword, or you want to prevent a name clash:

    @cli(name='next')
    def next_():
        # You can use `next` as command name now.


### How to use `nargs` positional argument

If you want to use a `narg` positional argument, you just need to define an
`*args` parameter:

    @cli
    def mycommand(root, *filenames):
        print('root:', root)
        for filename in filenames:
            print('Filename:', filename)


### How to control the number of possible optional arguments

For this, you should override the `nargs` option:

    @cli('param', nargs=4)
    def mycommand(param=[1, 2, 3, 4]):
        # Here you are sure you'll have received 4 values in `param`.
        pass


### How to define argument choices

You may want to control the choices for a mandatory positional argument:

    @cli('direction', choices=['top', 'down', 'left', 'right'])
    def go_to(direction):
        pass
