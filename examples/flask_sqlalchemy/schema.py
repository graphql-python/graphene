import graphene
from graphene import relay
from graphene.contrib.sqlalchemy import (SQLAlchemyConnectionField,
                                         SQLAlchemyNode)
from models import Department as DepartmentModel
from models import Employee as EmployeeModel

schema = graphene.Schema()


@schema.register
class Department(SQLAlchemyNode):

    class Meta:
        model = DepartmentModel


@schema.register
class Employee(SQLAlchemyNode):

    class Meta:
        model = EmployeeModel


class Query(graphene.ObjectType):
    node = relay.NodeField()
    all_employees = SQLAlchemyConnectionField(Employee)

schema.query = Query
