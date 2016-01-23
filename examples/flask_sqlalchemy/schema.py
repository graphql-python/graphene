import graphene
from graphene import relay
from graphene.contrib.sqlalchemy import SQLAlchemyNode
from models import Department as DepartmentModel, Employee as EmployeeModel

from database import db_session

schema = graphene.Schema(session=db_session)


@schema.register
class Department(SQLAlchemyNode):
    class Meta:
        model = DepartmentModel


@schema.register
class Employee(SQLAlchemyNode):
    class Meta:
        model = EmployeeModel


class Query(graphene.ObjectType):
    node = relay.NodeField(Department, Employee)

schema.query = Query
