from minicli import cli, run


@cli('deaf', help='If the person is deaf, we can write louder')
@cli('name', choices=['bob', 'mike', 'dave'])
async def greetings(name, age: int, deaf=False):
    """This is an example program

    :name: The name of the person we want to greet
    :age: The age of the person we want to greet
    """
    msg = "Hi {}! So you are {} years old".format(name, age)
    if deaf:
        msg = msg.upper()
    print(msg)


@cli
def say_bye(name):
    """Say bye.

    :name: The name of the person we say bye to.
    """
    print(f'Bye {name}!')


if __name__ == '__main__':
    run(deaf=False)
