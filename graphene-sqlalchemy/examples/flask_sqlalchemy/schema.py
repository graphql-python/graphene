import graphene
from graphene import relay
from graphene_sqlalchemy import (SQLAlchemyConnectionField,
                                 SQLAlchemyObjectType,
                                 SQLAlchemyNode)
from models import Department as DepartmentModel
from models import Employee as EmployeeModel
from models import Role as RoleModel


class Department(SQLAlchemyNode, SQLAlchemyObjectType):

    class Meta:
        model = DepartmentModel


class Employee(SQLAlchemyNode, SQLAlchemyObjectType):

    class Meta:
        model = EmployeeModel


class Role(SQLAlchemyNode, SQLAlchemyObjectType):

    class Meta:
        model = RoleModel


class Query(graphene.ObjectType):
    node = SQLAlchemyNode.Field()
    all_employees = SQLAlchemyConnectionField(Employee)
    all_roles = SQLAlchemyConnectionField(Role)
    role = graphene.Field(Role)


schema = graphene.Schema(query=Query, types=[Department, Employee, Role])
