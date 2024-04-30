import asyncio
from pathlib import Path

import pytest

from minicli import cli, run, wrap


def test_simple_arg_is_a_required_string(capsys):
    @cli
    def mycommand(param):
        print("Param is", param)

    run("mycommand", "myparam")
    out, err = capsys.readouterr()
    assert "Param is myparam" in out

    with pytest.raises(SystemExit) as e:
        run("mycommand")
        assert "error: the following arguments are required: param" in str(e)


def test_can_use_original_function(capsys):
    @cli
    def mycommand(param):
        print("Param is", param)

    mycommand("myparam")
    out, err = capsys.readouterr()
    assert "Param is myparam" in out


def test_underscore_are_replaced(capsys):
    @cli
    def my_command(param):
        print("Param is", param)

    run("my-command", "myparam")
    out, err = capsys.readouterr()
    assert "Param is myparam" in out

    run("my_command", "myparam")  # Name with _ should be kept as alias
    out, err = capsys.readouterr()
    assert "Param is myparam" in out


def test_kwarg_is_an_optional_param(capsys):
    @cli
    def mycommand(param="default"):
        print("Param is", param)

    run("mycommand", "--param", "value")
    out, err = capsys.readouterr()
    assert "Param is value" in out

    run("mycommand")
    out, err = capsys.readouterr()
    assert "Param is default" in out


def test_kwarg_with_none_default(capsys):
    @cli
    def mycommand(param=None):
        print("Param is", param if param else "empty")

    run("mycommand", "--param", "value")
    out, err = capsys.readouterr()
    assert "Param is value" in out

    run("mycommand")
    out, err = capsys.readouterr()
    assert "Param is empty" in out


def test_kwarg_with_empty_string_default(capsys):
    @cli
    def mycommand(param=""):
        print("Param is", param, type(param))

    run("mycommand", "--param", "value")
    out, err = capsys.readouterr()
    assert "Param is value <class 'str'>" in out

    run("mycommand", "--param", "9")
    out, err = capsys.readouterr()
    assert "Param is 9 <class 'str'>" in out

    run("mycommand")
    out, err = capsys.readouterr()
    assert "Param is  <class 'str'>" in out


def test_kwarg_value_type_is_used(capsys):
    @cli
    def mycommand(param=22):
        print("Param is", param)

    run("mycommand", "--param", "33")
    out, err = capsys.readouterr()
    assert "Param is 33" in out

    run("mycommand")
    out, err = capsys.readouterr()
    assert "Param is 22" in out

    with pytest.raises(SystemExit):
        run("mycommand", "--param", "notanint")
    out, err = capsys.readouterr()
    assert "argument --param/-p: invalid int value: 'notanint'" in err


def test_arg_can_be_typed_by_annotation(capsys):
    @cli
    def mycommand(param: int):
        print("Param is", param)

    run("mycommand", "22")
    out, err = capsys.readouterr()
    assert "Param is 22" in out

    with pytest.raises(SystemExit):
        run("mycommand", "notanint")
    out, err = capsys.readouterr()
    assert "argument param: invalid int value: 'notanint'" in err


def test_arg_can_use_arbitrary_callable_as_annotation_of_kwarg(capsys):
    def mytype(value):
        if value == "invalid":
            raise ValueError
        return value + value

    @cli
    def mycommand(param: mytype = None):
        print("Param is", param)

    run("mycommand", "--param", "foofoo")
    out, err = capsys.readouterr()
    assert "Param is foofoo" in out

    with pytest.raises(SystemExit):
        run("mycommand", "--param", "invalid")
    out, err = capsys.readouterr()
    assert """argument param: invalid loads value: 'invalid' in err"""


def test_arg_can_use_arbitrary_callable_as_annotation_as_arg(capsys):
    def mytype(value):
        if value == "invalid":
            raise ValueError
        return value + value

    @cli
    def mycommand(param: mytype):
        print("Param is", param)

    run("mycommand", "foofoo")
    out, err = capsys.readouterr()
    assert "Param is foofoo" in out

    with pytest.raises(SystemExit):
        run("mycommand", "invalid")
    out, err = capsys.readouterr()
    assert """argument param: invalid loads value: 'invalid' in err"""


def test_arg_can_use_path_as_annotation_of_arg(capsys):
    @cli
    def mycommand(param: Path):
        print("Param:", param, param.exists())

    run("mycommand", "/foo/bar")
    out, err = capsys.readouterr()
    assert "Param: /foo/bar False" in out


def test_first_line_of_docstring_is_used_for_command_doc(capsys):
    @cli
    def mycommand(param: int):
        """This is command doc"""
        print("Param is", param)

    with pytest.raises(SystemExit):
        run("--help")
    out, err = capsys.readouterr()
    assert "This is command doc" in out


def test_can_set_param_help_from_docstring(capsys):
    @cli
    def mycommand(myparam: int):
        """This is command doc

        :myparam: this is my param help
        """

    with pytest.raises(SystemExit):
        run("mycommand", "--help")
    out, err = capsys.readouterr()
    assert "this is my param help" in out


def test_can_set_param_help_from_cli_kwargs(capsys):
    @cli("myparam", help="this is my param help from kwargs")
    def mycommand(myparam: int):
        """This is command doc

        :myparam: this is my param help
        """

    with pytest.raises(SystemExit):
        run("mycommand", "--help")
    out, err = capsys.readouterr()
    assert "this is my param help from kwargs" in out


def test_can_set_param_choices_from_cli_kwargs(capsys):
    @cli("myparam", choices=[1, 2, 3, 4])
    def mycommand(myparam: int):
        print("Param is", myparam)

    run("mycommand", "2")
    out, err = capsys.readouterr()
    assert "Param is 2" in out

    with pytest.raises(SystemExit):
        run("mycommand", "5")
    out, err = capsys.readouterr()
    assert "myparam: invalid choice: 5 (choose from 1, 2, 3, 4)" in err


def test_can_override_two_params_from_cli_kwargs(capsys):
    @cli("myparam", help="myparam help")
    @cli("other", help="my other param help")
    def mycommand(myparam, other):
        pass

    with pytest.raises(SystemExit):
        run("mycommand", "--help")
    out, err = capsys.readouterr()
    assert "myparam help" in out
    assert "my other param help" in out
    with pytest.raises(SystemExit):
        run("--help")
    out, err = capsys.readouterr()
    assert out.count("mycommand") == 1


def test_args_are_mapped_nargs(capsys):
    @cli
    def mycommand(param, *params):
        print("Param:", param)
        for param in params:
            print("Param:", param)

    run("mycommand", "param1", "param2", "param3")
    out, err = capsys.readouterr()
    assert "Param: param1" in out
    assert "Param: param2" in out
    assert "Param: param3" in out


def test_can_call_cli_without_arguments(capsys):
    @cli()  # Calling the decorator without args nor kwargs.
    def mycommand(param):
        print("Param is", param)

    run("mycommand", "myparam")
    out, err = capsys.readouterr()
    assert "Param is myparam" in out


def test_can_decorate_async_functions(capsys):
    @cli
    async def mycommand(param):
        print("Param is", param)

    run("mycommand", "myparam")
    out, err = capsys.readouterr()
    assert "Param is myparam" in out

    asyncio.get_event_loop().run_until_complete(mycommand("myparam"))
    out, err = capsys.readouterr()
    assert "Param is myparam" in out


def test_can_mix_async_and_normal_functions(capsys):
    @cli
    async def mycommand(param):
        print("Param is", param)

    @cli
    def myothercommand(param):
        print("Other command param is", param)

    run("mycommand", "myparam")
    out, err = capsys.readouterr()
    assert "Param is myparam" in out

    run("myothercommand", "myparam")
    out, err = capsys.readouterr()
    assert "Other command param is myparam" in out

    asyncio.get_event_loop().run_until_complete(mycommand("myparam"))
    out, err = capsys.readouterr()
    assert "Param is myparam" in out

    myothercommand("myparam")
    out, err = capsys.readouterr()
    assert "Other command param is myparam" in out


def test_can_append_to_list(capsys):
    @cli
    def mycommand(param=[]):
        print(param)

    run("mycommand", "--param", "foo", "--param", "bar")
    out, err = capsys.readouterr()
    assert "['foo', 'bar']" in out


def test_can_override_list_nargs(capsys):
    @cli("param", nargs=4)
    def mycommand(param=[1, 2, 3, 4]):
        print(param)

    run("mycommand", "--param", "1", "2", "3", "4")
    out, err = capsys.readouterr()
    assert "['1', '2', '3', '4']" in out

    with pytest.raises(SystemExit):
        run("mycommand", "--param", "1", "2", "3")
    out, err = capsys.readouterr()
    assert "argument --param/-p: expected 4 arguments" in err


def test_can_override_command_name(capsys):
    @cli(name="import")
    def import_(param):
        print(param)

    run("import", "foo")
    out, err = capsys.readouterr()
    assert "foo" in out


def test_can_override_arg_name(capsys):
    @cli("from_", name="from")
    def mycommand(from_=None):
        print(from_)

    run("mycommand", "--from", "foo")
    out, err = capsys.readouterr()
    assert "foo" in out


def test_can_override_param_with_same_name_as_command(capsys):
    @cli("mycommand", choices=["foo", "bar"])
    def mycommand(mycommand):
        print(mycommand)

    run("mycommand", "foo")
    out, err = capsys.readouterr()
    assert "foo" in out

    with pytest.raises(SystemExit):
        run("mycommand", "baz")
    out, err = capsys.readouterr()
    assert "mycommand: invalid choice: 'baz' (choose from 'foo', 'bar')" in err


def test_wrappers(capsys):
    @cli
    def mycommand(mycommand):
        print(mycommand)

    @wrap
    def my_wrapper():
        print("before")
        yield
        print("after")

    run("mycommand", "during")
    out, err = capsys.readouterr()
    assert "before\nduring\nafter\n" in out


def test_wrapper_cannot_omit_yield(capsys):
    @cli
    def mycommand(mycommand):
        print(mycommand)

    with pytest.raises(ValueError):

        @wrap
        def my_wrapper():
            print("before")


def test_wrappers_can_be_async(capsys):
    @cli
    def mycommand(mycommand):
        print(mycommand)

    @wrap
    async def my_wrapper():
        print("before")
        yield
        print("after")

    run("mycommand", "during")
    out, err = capsys.readouterr()
    assert "before\nduring\nafter\n" in out


def test_wrappers_can_access_globals(capsys):
    @cli
    def mycommand(mycommand):
        print(mycommand)

    @wrap
    def my_wrapper(host):
        print("before", host)
        yield
        print("after", host)

    run("mycommand", "during", host="example.org")
    out, err = capsys.readouterr()
    assert "before example.org\nduring\nafter example.org\n" in out

    run("mycommand", "during", "--host", "example.org", host="default")
    out, err = capsys.readouterr()
    assert "before example.org\nduring\nafter example.org\n" in out


def test_cmd_can_access_globals(capsys):
    @cli
    def mycommand(param, host=None):
        print(param, host)

    run("mycommand", "param", host="example.org")
    out, err = capsys.readouterr()
    assert "param example.org" in out

    run("mycommand", "param", "--host", "example.org", host="default")
    out, err = capsys.readouterr()
    assert "param example.org" in out


def test_can_chain_command_calls(capsys):
    @cli
    def mycommand(param, optional=False):
        print("Param is", param)

    @cli
    def myothercommand(param):
        print("Other command param is", param)

    @wrap
    def my_wrapper():
        print("before")
        yield
        print("after")

    run("mycommand", "myparam")
    out, err = capsys.readouterr()
    assert "Param is myparam" in out
    assert out.count("before") == 1
    assert out.count("after") == 1

    run("myothercommand", "myparam")
    out, err = capsys.readouterr()
    assert "Other command param is myparam" in out
    assert out.count("before") == 1
    assert out.count("after") == 1

    run("myothercommand", "myparam", "mycommand", "myparam", "--optional")
    out, err = capsys.readouterr()
    assert "Param is myparam" in out
    assert "Other command param is myparam" in out
    assert out.count("before") == 1
    assert out.count("after") == 1

    run("mycommand", "myparam", "--optional", "myothercommand", "myparam")
    out, err = capsys.readouterr()
    assert "Param is myparam" in out
    assert "Other command param is myparam" in out
    assert out.count("before") == 1
    assert out.count("after") == 1

    run("mycommand", "myparam", "myothercommand", "myparam")
    out, err = capsys.readouterr()
    assert "Param is myparam" in out
    assert "Other command param is myparam" in out
    assert out.count("before") == 1
    assert out.count("after") == 1


def test_do_not_call_any_command_with_unkown_extra(capsys):
    @cli
    def mycommand(param):
        print(param)

    run("mycommand", "success")
    out, err = capsys.readouterr()
    assert "success" in out

    with pytest.raises(SystemExit):
        run("mycommand", "success", "failed")
    out, err = capsys.readouterr()
    assert "success" not in out
    assert "failed" not in out


def test_run_without_declaring_command(capsys):
    def mycommand(param):
        print(param)
        return

    run(mycommand, "a param")
    out, err = capsys.readouterr()
    assert "a param" in out


def test_single_command_cli_with_args(capsys):
    @cli("param", nargs=4)
    def mycommand(param=[1, 2, 3, 4]):
        print(param)

    run(mycommand, "--param", "1", "2", "3", "4")
    out, err = capsys.readouterr()
    assert "['1', '2', '3', '4']" in out

    with pytest.raises(SystemExit):
        run(mycommand, "--param", "1", "2", "3")
    out, err = capsys.readouterr()
    assert "argument --param/-p: expected 4 arguments" in err
