import graphene
from graphene import relay
from graphene_sqlalchemy import (SQLAlchemyConnectionField,
                                 SQLAlchemyObjectType)
from models import Department as DepartmentModel
from models import Employee as EmployeeModel
from models import Role as RoleModel


class Department(SQLAlchemyObjectType):

    class Meta:
        model = DepartmentModel
        interfaces = (relay.Node, )


class Employee(SQLAlchemyObjectType):

    class Meta:
        model = EmployeeModel
        interfaces = (relay.Node, )


class Role(SQLAlchemyObjectType):

    class Meta:
        model = RoleModel
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    employee_connection = relay.Connection.for_type(Employee)
    role_connection = relay.Connection.for_type(Role)
    all_employees = SQLAlchemyConnectionField(employee_connection)
    all_roles = SQLAlchemyConnectionField(role_connection)
    role = graphene.Field(Role)


schema = graphene.Schema(query=Query, types=[Department, Employee, Role])
