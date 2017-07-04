import pytest

from minicli import cli, run


def test_simple_arg_is_a_required_string(capsys):

    @cli
    def mycommand(param):
        print("Param is", param)

    run('mycommand', 'myparam')
    out, err = capsys.readouterr()
    assert "Param is myparam" in out

    with pytest.raises(SystemExit) as e:
        run('mycommand')
        assert "error: the following arguments are required: param" in str(e)


def test_kwarg_is_an_optional_param(capsys):

    @cli
    def mycommand(param='default'):
        print("Param is", param)

    run('mycommand', '--param', 'value')
    out, err = capsys.readouterr()
    assert "Param is value" in out

    run('mycommand')
    out, err = capsys.readouterr()
    assert "Param is default" in out


def test_kwarg_value_type_is_used(capsys):

    @cli
    def mycommand(param=22):
        print("Param is", param)

    run('mycommand', '--param', '33')
    out, err = capsys.readouterr()
    assert "Param is 33" in out

    run('mycommand')
    out, err = capsys.readouterr()
    assert "Param is 22" in out

    with pytest.raises(SystemExit) as e:
        run('mycommand', '--param', 'notanint')
        assert "argument --param/-p: invalid int value: 'notanint'" in str(e)


def test_arg_can_be_typed_by_annotation(capsys):

    @cli
    def mycommand(param: int):
        print("Param is", param)

    run('mycommand', '22')
    out, err = capsys.readouterr()
    assert "Param is 22" in out

    with pytest.raises(SystemExit) as e:
        run('mycommand', 'notanint')
        assert "argument param: invalid int value: 'notanint'" in str(e)


def test_first_line_of_docstring_is_used_for_command_doc(capsys):

    @cli
    def mycommand(param: int):
        """This is command doc"""
        print("Param is", param)

    with pytest.raises(SystemExit):
        run('--help')
    out, err = capsys.readouterr()
    assert "This is command doc" in out


def test_can_set_param_help_from_docstring(capsys):

    @cli
    def mycommand(myparam: int):
        """This is command doc

        :myparam: this is my param help
        """

    with pytest.raises(SystemExit):
        run('mycommand', '--help')
    out, err = capsys.readouterr()
    assert "this is my param help" in out


def test_args_are_mapped_nargs(capsys):

    @cli
    def mycommand(param, *params):
        print('Param:', param)
        for param in params:
            print('Param:', param)

    run('mycommand', 'param1', 'param2', 'param3')
    out, err = capsys.readouterr()
    assert "Param: param1" in out
    assert "Param: param2" in out
    assert "Param: param3" in out
