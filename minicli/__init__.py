import argparse
import asyncio
import inspect


NO_DEFAULT = inspect._empty
NARGS = ...

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(title='Available commands', metavar='')

GLOBALS = {}


class Cli:

    def __init__(self, command, **extra):
        self.extra = extra
        self.command = command
        self.inspect()
        self.init_parser()
        self.set_globals()
        command._cli = self

    def __call__(self, *args, **kwargs):
        """Run original command."""
        try:
            res = self.command(*args, **kwargs)
            if self.async:
                asyncio.get_event_loop().run_until_complete(res)
        except KeyboardInterrupt:
            pass

    def invoke(self, parsed):
        """Run command from command line args."""
        kwargs = {}
        args = []
        for name, parameter in self.spec.parameters.items():
            value = getattr(parsed, name)
            if parameter.kind == parameter.VAR_POSITIONAL:
                args.extend(value)
            elif parameter.default == NO_DEFAULT:
                args.append(value)
            else:
                kwargs[name] = value
        kwargs.update(self.parse_globals(parsed))
        return self(*args, **kwargs)

    def set_globals(self):
        for name, kwargs in GLOBALS.items():
            if not isinstance(kwargs, dict):
                kwargs = {'default': kwargs}
            self.add_argument(name, **kwargs)

    def parse_globals(self, parsed):
        return {k: getattr(parsed, k, None) for k in GLOBALS.keys()
                if hasattr(parsed, k)}

    @property
    def name(self):
        return self.command.__name__

    @property
    def help(self):
        return self.command.__doc__ or ''

    @property
    def short_help(self):
        return self.help.split('\n\n')[0]

    def inspect(self):
        self.__doc__ = inspect.getdoc(self.command)
        self.spec = inspect.signature(self.command)
        self.async = inspect.iscoroutinefunction(self.command)

    def parse_parameter_help(self, name):
        try:
            return (self.help.split(':{}:'.format(name), 1)[1]
                             .split('\n')[0].strip())
        except IndexError:
            return ''

    def init_parser(self):
        kwargs = {
            'name': self.name,
            'help': self.short_help,
            'conflict_handler': 'resolve'
        }
        kwargs.update(self.extra.get('__self__', {}))
        self.parser = subparsers.add_parser(**kwargs)
        self.set_defaults(func=self.invoke)
        for name, parameter in self.spec.parameters.items():
            kwargs = {}
            default = parameter.default
            if parameter.kind == parameter.VAR_POSITIONAL:
                default = NARGS
            type_ = parameter.annotation
            if type_ != inspect._empty:
                kwargs['type'] = type_
            kwargs.update(self.extra.get(name, {}))
            self.add_argument(name, default, **kwargs)

    def add_argument(self, name, default=NO_DEFAULT, **kwargs):
        if 'help' not in kwargs:
            kwargs['help'] = self.parse_parameter_help(name)
        args = [name]
        if default not in (NO_DEFAULT, NARGS):
            if '_' not in name:
                args.append('-{}'.format(name[0]))
            args[0] = '--{}'.format(name.replace('_', '-'))
            kwargs['dest'] = name
            kwargs['default'] = default
            type_ = kwargs.pop('type', type(default))
            if type_ == bool:
                action = 'store_false' if default else 'store_true'
                kwargs['action'] = action
            elif type_ in (int, str):
                kwargs['type'] = type_
            elif type_ in (list, tuple):
                kwargs['nargs'] = kwargs.get('nargs', '*')
            elif callable(default):
                kwargs['type'] = type_
                kwargs['default'] = ''
        elif default == NARGS:
            kwargs['nargs'] = '*'
        self.parser.add_argument(*args, **kwargs)

    def set_defaults(self, **kwargs):
        self.parser.set_defaults(**kwargs)


def cli(*args, **kwargs):
    if not args:
        # User-friendlyness: allow using @cli() without any argument.
        if kwargs:  # Overriding parser arguments with only kwargs.
            return lambda f: cli(f, '__self__', **kwargs)
        return cli
    if not callable(args[0]):
        # We are overriding an argument from the decorator.
        return lambda f: cli(f, *args, **kwargs)
    func = args[0]
    extra = {}
    if hasattr(func, '_cli') and len(args) > 1 and kwargs:
        # Chaining cli(xxx) calls.
        extra = func._cli.extra
        # We don't know how to update an existing action, so let's reset it
        # totally with new signature.
        for idx, action in enumerate(subparsers._choices_actions[:]):
            if action.dest == func._cli.name:
                del subparsers._choices_actions[idx]
    if len(args) > 1:
        extra[args[1]] = kwargs
    Cli(func, **extra)
    return func


def run(*args):
    parsed = parser.parse_args(args or None)
    if hasattr(parsed, 'func'):
        parsed.func(parsed)
    else:
        # No argument given, just display help.
        parser.print_help()
