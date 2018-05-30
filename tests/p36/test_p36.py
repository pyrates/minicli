# Tests that must be run only with Python >= 3.6
from minicli import cli, run, wrap


def test_wrappers_can_be_async(capsys):

    @cli
    def mycommand(mycommand):
        print(mycommand)

    @wrap
    async def my_wrapper():
        print('before')
        yield
        print('after')

    run('mycommand', 'during')
    out, err = capsys.readouterr()
    assert 'before\nduring\nafter\n' in out
