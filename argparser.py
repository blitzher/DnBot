
def parse(message:str, args:list, kwargs:dict):

    d = kwargs

    splitted = message.split(" ")
    print(splitted)
    print(len(splitted), len(args))
    assert len(splitted) >= len(args), ("Must fill all args: %s" % args)

    for argname, argval in zip(args,splitted):
        d[argname] = argval
    
    keyword_message = splitted[len(args):]

    for obj in keyword_message:
        assert ':' in obj, "Keyword arguments must contain a ':'"
        key, val = obj.split(":")
        assert key in d, "Cannot assign new keyword to dict"
        d[key] = val

    return d
        
