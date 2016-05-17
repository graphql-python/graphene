import graphene

class Tea(graphene.ObjectType):
    name = graphene.String()
    steeping_time = graphene.Int()

TEAS = [
    Tea(name='Earl Grey Blue Star', steeping_time=5),
    Tea(name='Milk Oolong', steeping_time=3),
    Tea(name='Gunpowder Golden Temple', steeping_time=3),
    Tea(name='Assam Hatimara', steeping_time=5),
    Tea(name='Bancha', steeping_time=2),
    Tea(name='Ceylon New Vithanakande', steeping_time=5),
    Tea(name='Golden Tip Yunnan', steeping_time=5),
    Tea(name='Jasmine Phoenix Pearls', steeping_time=3),
    Tea(name='Kenya Milima', steeping_time=5),
    Tea(name='Pu Erh First Grade', steeping_time=4),
    Tea(name='Sencha Makoto', steeping_time=3),
]

class Store(graphene.ObjectType):
    teas = graphene.List(Tea, order_by=graphene.String())

    def resolve_teas(self, args, context, info):
        order_by = args.get("order_by")
        if order_by == "steepingTime":
            return sorted(self.teas, key=lambda tea: tea.steeping_time)
        elif order_by == "name":
            return sorted(self.teas, key=lambda tea: tea.name)
        return self.teas

class Query(graphene.ObjectType):
    store = graphene.Field(Store)

    def resolve_store(self, args, context, info):
        return Store(teas=TEAS) 

schema = graphene.Schema(query=Query)