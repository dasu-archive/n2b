# repositories/attribute_repository.py
from sqlalchemy.orm import Session, aliased
from database.models import Attributes, AttributesMapping

def get_mappings_by_notion_id(session: Session, category_id: str, group_id) -> AttributesMapping:
    CategoryAttr = aliased(Attributes)
    GroupAttr = aliased(Attributes)

    result = (
        session.query(AttributesMapping)
        .join(CategoryAttr, AttributesMapping.category_id == CategoryAttr.id)
        .join(GroupAttr, AttributesMapping.group_id == GroupAttr.id)
        .filter(
            (CategoryAttr.notion_attribute_id == category_id)
            & (GroupAttr.notion_attribute_id == group_id)
        )
        .first()
    )
    return result

def get_attribute_by_notion_attribute_id(session: Session, attribute_id: int, kind: str) -> Attributes:
    return session.query(Attributes).filter_by(
        notion_attribute_id=attribute_id,
        attribute_kind=kind).first()

