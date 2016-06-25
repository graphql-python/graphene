from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import backref, relationship

# Uncomment import below for postgresql tests
# import uuid
# from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON, JSONB, HSTORE, ARRAY
# from sqlalchemy.sql.expression import text

from database import Base


class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(Integer, primary_key=True)
    name = Column(String)


class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # Use default=func.now() to set the default hiring time
    # of an Employee to be the current time when an
    # Employee record was created
    hired_on = Column(DateTime, default=func.now())
    department_id = Column(Integer, ForeignKey('department.id'))
    role_id = Column(Integer, ForeignKey('roles.role_id'))

    # Uncomment below for postgresql specific fields testing
    # uuid = Column(UUID(), server_default=text("uuid_generate_v4()"))
    # is_active = Column(ENUM('Yes', 'No', name='is_active'), default="Yes")
    # json_data = Column(JSON())
    # jsonb_data = Column(JSONB())
    # hstore_data = Column(HSTORE())
    # articles = Column(ARRAY(Integer))

    # Use cascade='delete,all' to propagate the deletion of a Department onto its Employees
    department = relationship(
        Department,
        backref=backref('employees',
                        uselist=True,
                        cascade='delete,all'))
    role = relationship(
        Role,
        backref=backref('roles',
                        uselist=True,
                        cascade='delete,all'))
