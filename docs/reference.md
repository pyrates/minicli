# Reference

## cli

`cli` is the main API of minicli, it's a decorator to help you create
[argparse](https://docs.python.org/3/library/argparse.html) command easily.

You basically can call it in three ways — without any argument, with only `kwargs`,
with a `name` argument and `kwargs`:


### `@cli` (no `*args`, no `**kwargs`)

In this case, minicli will extrapolate the command name and the arguments names
and types for the decorated function. Basically, all `*args` will be mapped to
positional arguments, and `**kwargs` will be mapped to `optional` ones.

For example, this will generate a command called `mycommand`, with one
positional argument named `action`, and one optional argument of type `int`
named `count`:

    @cli
    def mycommand(action, count=10):
        pass

This is the more common usage of `@cli`. But sometimes, you want better
control. This is done by passing `argparse` arguments to `@cli`, see below.

*Note: `@cli()` will also work.*


### `@cli(**kwargs)` (kwargs, but no args)

Those `kwargs` will override the `kwargs` passed to
[add_parser](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser).


For example, you may want to override the command name (maybe because your are
using a python reserved keyword, or you want to prevent a name clash):

    @cli(name='next')
    def next_():
        # You can use `next` as command name now.


### `cli(name, **kwargs)`

Those `kwargs` will override the `kwargs` passed to
[add_argument](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument)
for the argument `name`.

For example you may want to control the choices of a mandatory positional
argument:

    @cli('direction', choices=['top', 'down', 'left', 'right'])
    def go_to(direction):
        pass


You can chain the calls to `@cli` as needed:

    @cli('speed', choices=range(5, 10))
    @cli('direction', choices=['top', 'down', 'left', 'right'])
    def go_to(direction, speed: int):
        pass

See [how-to guides](how-to.md) for concrete usage examples.


## run

`run` will call `argparse` for you. You generally want to call it like this:

    if __name__ == '__main__':
        run()
