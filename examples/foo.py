from pprint import pprint

from pydantic import ConfigDict
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

from appboot.repository import Repository
from appboot.schema import ModelSchema
from appboot.utils import make_model_by_obj

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, doc="姓名")
    email = Column(String, unique=True)

    addresses = relationship("Address", back_populates="user")


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)

    user = relationship("User", back_populates="addresses")


class RepositoryA(Repository["Demo"]):
    pass


class Demo(ModelSchema):
    user_id: int = 1

    class Meta:
        model = Address
        exclude_fields = ["zip"]
        repository_class = RepositoryA

    model_config = ConfigDict(validate_assignment=True)


def main():
    pprint(Demo.__fields__)
    d = make_model_by_obj(Demo, {"id": 1})
    print(d.dict(exclude_defaults=True))
    dao = Demo.objects
    print(dao)


if __name__ == "__main__":
    main()
