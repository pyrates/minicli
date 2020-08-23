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


## How to override the command name

You may want to override the command name, maybe because your are
using a python reserved keyword, or you want to prevent a name clash:

    @cli(name='import')
    def import_():
        # You can use `import` as command name now.


## How to override an argument name

You may want to override an argument name, maybe because your are
using a python reserved keyword:

    @cli("from_", name='from')  # Pass here any argparse argument you want to control.
    def mycommmand(from_=None):
        # You can use `from` as argument now.
        # mycommand --from foobar


## How to use `nargs` positional argument

If you want to use a `narg` positional argument, you just need to define an
`*args` parameter:

    @cli
    def mycommand(root, *filenames):
        print('root:', root)
        for filename in filenames:
            print('Filename:', filename)


## How to control the number of possible optional arguments

For this, you should override the `nargs` option:

    @cli('param', nargs=4)
    def mycommand(param=[1, 2, 3, 4]):
        # Here you are sure you'll have received 4 values in `param`.
        pass


## How to define argument choices

You may want to control the choices for a mandatory positional argument:

    @cli('direction', choices=['top', 'down', 'left', 'right'])
    def go_to(direction):
        pass


## How to deal with global parameters

You may have parameters used all over your commands, and you want to define them
only once. This can be done through the `run`
[call](reference.md#global-parameters):

    import getpass

    @cli
    def my_command(username=None):
        # do something with username


    @cli
    def my_other_command(username=None):
        # do something with username

    run(username=getpass.getuser())


## How to create a global DB connection

If all of your commands use a single DB connection (or it can be a single SSH
connection…), you can manage it using the [wrap](reference.md#wrap) decorator:

    app = MyApp()

    @cli
    def my_command():
        # do something with app.connection


    @cli
    def my_other_command():
        # do something with app.connection


    @wrap
    async def wrapper(dbname, dbuser):  # Of course it works without async.
        app.connection = await mydb.connect(dbname, dbuser)
        yield
        await app.connection.close()


    run(dbname='default', dbuser='default')
