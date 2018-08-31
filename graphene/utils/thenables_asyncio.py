def await_and_execute(obj, on_resolve):
    async def build_resolve_async():
        return on_resolve(await obj)

    return build_resolve_async()
