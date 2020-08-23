import argparse
import asyncio
import inspect

NO_DEFAULT = inspect._empty
NARGS = ...
_wrapper_functions = []
_wrapper_generators = []
_registry = []


class Cli:

    def __init__(self, command, **extra):
        self.extra = extra
        self.command = command
        self.inspect()
        if not hasattr(command, '_cli'):
            command._cli = self
            _registry.append(self)

    def __call__(self, *args, **kwargs):
        """Run original command."""
        try:
            res = self.command(*args, **kwargs)
            if self._async:
                asyncio.get_event_loop().run_until_complete(res)
        except KeyboardInterrupt:
            pass

    def invoke(self, parsed, **shared):
        """Run command from command line args."""
        kwargs = {}
        args = []
        for name, parameter in self.spec.parameters.items():
            value = shared.get(name, getattr(parsed, name))
            if parameter.kind == parameter.VAR_POSITIONAL:
                args.extend(value)
            elif parameter.default == NO_DEFAULT:
                args.append(value)
            else:
                kwargs[name] = value
        return self(*args, **kwargs)

    @property
    def help(self):
        return self.command.__doc__ or ''

    @property
    def short_help(self):
        return self.help.split('\n\n')[0]

    def inspect(self):
        self.__doc__ = inspect.getdoc(self.command)
        self.spec = inspect.signature(self.command)
        self._async = inspect.iscoroutinefunction(self.command)

    def parse_parameter_help(self, name):
        try:
            return (self.help.split(':{}:'.format(name), 1)[1]
                             .split('\n')[0].strip())
        except IndexError:
            return ''

    def init_parser(self, subparsers):
        kwargs = {
            'help': self.short_help,
            'conflict_handler': 'resolve'
        }
        name = self.command.__name__
        if '_' in name:
            kwargs['aliases'] = [name]
            name = name.replace('_', '-')
        kwargs['name'] = name
        kwargs.update(self.extra.get('__self__', {}))
        self.parser = subparsers.add_parser(**kwargs)
        self.set_defaults(func=self.invoke)
        for arg_name, parameter in self.spec.parameters.items():
            kwargs = {}
            default = parameter.default
            if parameter.kind == parameter.VAR_POSITIONAL:
                default = NARGS
            type_ = parameter.annotation
            if type_ != inspect._empty:
                kwargs['type'] = type_
            kwargs.update(self.extra.get(arg_name, {}))
            if 'help' not in kwargs:
                kwargs['help'] = self.parse_parameter_help(arg_name)
            if 'default' not in kwargs:
                kwargs['default'] = default
            self.add_argument(arg_name, **kwargs)

    def add_argument(self, arg_name, **kwargs):
        args, kwargs = make_argument(arg_name, **kwargs)
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
    if len(args) > 1:
        extra[args[1]] = kwargs
    Cli(func, **extra)
    return func


def run(*input, **shared):
    parser = argparse.ArgumentParser(add_help=False)
    for arg_name, kwargs in shared.items():
        if not isinstance(kwargs, dict):
            kwargs = {'default': kwargs}
        args, kwargs = make_argument(arg_name, **kwargs)
        parser.add_argument(*args, **kwargs)
    # shared must be parsed before actual commands so they can be passed to
    # before wrapper
    parsed, extras = parser.parse_known_args(input or None)
    shared = {k: getattr(parsed, k, None) for k in shared.keys()
              if hasattr(parsed, k)}
    # No command is known when calling parse_known_args, prevent argparse to
    # display the help and exit.
    parser.add_argument('-h', '--help', action='store_true',
                        help='Show this help message and exit')
    subparsers = parser.add_subparsers(title='Available commands', metavar='')
    for cmd in _registry:
        cmd.init_parser(subparsers)

    # Parse all possible args before calling any func, to prevent considering
    # a wrong argument passed by mistake as a chained command.
    commands = []
    while extras:
        command, extras = parser.parse_known_args(args=extras)
        if not command or not hasattr(command, 'func'):
            # No argument given, just display help.
            parser.print_help()
            parser.exit()  # Mimic original behaviour.
        commands.append(command)

    # Now call commands for real.
    prepare_wrappers(**shared)
    call_wrappers()
    try:
        for command in commands:
            command.func(command, **shared)
    finally:
        call_wrappers()


def wrap(func):
    if not (inspect.isgeneratorfunction(func)
            or inspect.isasyncgenfunction(func)):
        raise ValueError(f'"{func}" needs to yield')
    _wrapper_functions.append(func)
    return func


def call_wrappers():
    for wrapper in _wrapper_generators:
        try:
            if inspect.isasyncgen(wrapper):
                fut = wrapper.__anext__()
                asyncio.get_event_loop().run_until_complete(fut)
            else:
                next(wrapper)
        except (StopIteration, StopAsyncIteration):
            pass


def prepare_wrappers(**shared):
    for func in _wrapper_functions:
        spec = inspect.signature(func)
        kwargs = {}
        args = []
        for name, parameter in spec.parameters.items():
            value = shared.get(name)
            if parameter.kind == parameter.VAR_POSITIONAL:
                args.extend(value)
            elif parameter.default == NO_DEFAULT:
                args.append(value)
            else:
                kwargs[name] = value
        # Execute each wrapper to get the generator.
        _wrapper_generators.append(func(*args, **kwargs))


def make_argument(arg_name, default=NO_DEFAULT, **kwargs):
    name = kwargs.pop("name", arg_name)
    args = [name]
    if default not in (NO_DEFAULT, NARGS):
        if '_' not in name and name[0] != 'h':
            args.append('-{}'.format(name[0]))
        args[0] = '--{}'.format(name.replace('_', '-'))
        kwargs['dest'] = arg_name
        kwargs['default'] = default
        type_ = kwargs.pop('type',
                           type(default) if default is not None else None)
        if type_ == bool:
            action = 'store_false' if default else 'store_true'
            kwargs['action'] = action
        elif type_ in (list, tuple):
            kwargs['nargs'] = kwargs.get('nargs', '*')
        elif callable(type_):
            kwargs['type'] = type_
        elif callable(default):
            kwargs['type'] = type_
            kwargs['default'] = ''
    elif default == NARGS:
        kwargs['nargs'] = '*'
    return args, kwargs
