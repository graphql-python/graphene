import graphene
from graphene import relay
from graphene.contrib.sqlalchemy import (SQLAlchemyConnectionField,
                                         SQLAlchemyNode)
from models import Department as DepartmentModel
from models import Employee as EmployeeModel
from models import Role as RoleModel

schema = graphene.Schema()


@schema.register
class Department(SQLAlchemyNode):

    class Meta:
        model = DepartmentModel


@schema.register
class Employee(SQLAlchemyNode):

    class Meta:
        model = EmployeeModel


@schema.register
class Role(SQLAlchemyNode):

    class Meta:
        model = RoleModel
        identifier = 'role_id'


class Query(graphene.ObjectType):
    node = relay.NodeField(Employee)
    all_employees = SQLAlchemyConnectionField(Employee)
    all_roles = SQLAlchemyConnectionField(Role)
    role = relay.NodeField(Role)

schema.query = Query
