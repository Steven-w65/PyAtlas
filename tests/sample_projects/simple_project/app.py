from helpers import Greeter


def run(name: str) -> str:
    greeter = Greeter()
    if name:
        return greeter.greet(name)
    return "Hello"

