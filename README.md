# Minicli

Expose functions in the command line. Minimalist and pythonic.

Supports annotations and async functions.


# Usage

Example program:

    from minicli import cli, run


    @cli
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

Example usage:

    $ myprogram.py --help
    usage: myprogram.py [-h]  ...

    optional arguments:
      -h, --help  show this help message and exit

    Available commands:

        greetings
                  This is an example program

    $ myprogram.py greetings --help
    usage: __init__.py greetings [-h] [--deaf] name age

    positional arguments:
      name        The name of the person we want to greet
      age         The age of the person we want to greet

    optional arguments:
      -h, --help  show this help message and exit
      --deaf, -d  If the person is deaf, we can write louder

    $ myprogram.py greetings bob 19
    Hi bob! So you are 19 years old

    $ myprogram.py greetings bob 19 --deaf
    HI BOB! SO YOU ARE 19 YEARS OLD

    $ myprogram.py greetings bob nineteen
    usage: myprogram.py greetings [-h] [--deaf] name age
    myprogram.py greetings: error: argument age: invalid int value: 'nineteen'
