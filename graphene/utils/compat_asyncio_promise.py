import promise

def promisify(resolved):
    try:
        import asyncio
        if isinstance(resolved, asyncio.Future) or \
            asyncio.iscoroutine(resolved):
            return promise.promisify(resolved)
    except:
        pass

    return resolved
