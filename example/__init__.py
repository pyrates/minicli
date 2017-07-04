from minicli import cli, run


@cli
# @cli('deaf', help='This is my deaf help')
def greetings(name, age: int, deaf=False):
    """This is an example program

    :name: The name of the person we want to greet
    :age: The age of the person we want to greet
    :deaf: If the person is deaf, we can write louder
    """
    msg = "Hi {}! So you are {} years old".format(name, age)
    if deaf:
        msg = msg.upper()
    print(msg)


if __name__ == '__main__':
    run()
