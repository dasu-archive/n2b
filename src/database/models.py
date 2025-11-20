from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from database.mysql_conf import engine

Base = declarative_base()


class Attributes(Base):
    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notion_attribute_id = Column(String(100), unique=True, nullable=False)
    notion_attribute_name = Column(String(100))
    tistory_attribute_name = Column(String(100))
    attribute_kind = Column(String(100), nullable=False)  
    changed_name = Column(Boolean, nullable=False, default=False)

    # AttributesMapping과의 관계
    categories = relationship(
        "AttributesMapping",
        foreign_keys="AttributesMapping.category_id",
        back_populates="category",
        cascade="all, delete-orphan"
    )
    groups = relationship(
        "AttributesMapping",
        foreign_keys="AttributesMapping.group_id",
        back_populates="group",
        cascade="all, delete-orphan"
    )


class AttributesMapping(Base):
    __tablename__ = "attributes_mapping"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("attributes.id"))
    group_id = Column(Integer, ForeignKey("attributes.id"))
    tistory_id = Column(Integer, default=0)
    # Attributes와 관계
    category = relationship(
        "Attributes",
        foreign_keys=[category_id],
        back_populates="categories"
    )
    group = relationship(
        "Attributes",
        foreign_keys=[group_id],
        back_populates="groups"
    )




# 초기 테이블 생성
def init_tables():
    Base.metadata.create_all(bind=engine)