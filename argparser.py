from discord import Message


def parse(message: Message, args: list, kwargs: dict):

    d = kwargs

    splitted = message.content.split(" ")[1:]
    print(splitted)
    assert len(splitted) >= len(args), ("Must fill all args: %s" % args)

    for argname, argval in zip(args, splitted):
        d[argname] = argval

    keyword_args = splitted[len(args):]

    for obj in keyword_args:
        assert '=' in obj, "Keyword arguments must contain a '='"
        key, val = obj.split("=")
        assert key in d, "Cannot assign new keyword to dict"
        d[key] = val

    return d
