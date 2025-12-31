# repositories/attribute_repository.py
from sqlalchemy.orm import Session, aliased
from n2b.database.models import Attributes, AttributesMapping

def get_mappings_by_notion_id(session: Session, category_id: str, group_id: str | None = None, parent_id: int | None = None) -> AttributesMapping:
    CategoryAttr = aliased(Attributes)
    GroupAttr = aliased(Attributes)

    filters = [
            CategoryAttr.notion_attribute_id == category_id
        ]

    # Group 조건 추가
    if group_id is not None:
        filters.append(GroupAttr.notion_attribute_id == group_id)
    # parent 조건추가
    if parent_id is None:
        filters.append(AttributesMapping.parent_id.is_(None))
    else:
        filters.append(AttributesMapping.parent_id == parent_id)
        
    result = (
        session.query(AttributesMapping)
        .join(CategoryAttr, AttributesMapping.category_id == CategoryAttr.id, isouter=True)
        .join(GroupAttr, AttributesMapping.group_id == GroupAttr.id, isouter=True)
        .filter(*filters)
    )
    return result.first()

def get_attribute_by_notion_attribute_id(session: Session, attribute_id: int, kind: str) -> Attributes:
    return session.query(Attributes).filter_by(
        notion_attribute_id=attribute_id,
        attribute_kind=kind).first()

def count_mappings_by_parent_id(session: Session, parent_id: int | None = None) -> int:
    filters = []
    if parent_id is None:
        filters.append(AttributesMapping.parent_id.is_(None))
    else:
        filters.append(AttributesMapping.parent_id == parent_id)
    return (
        session.query(AttributesMapping)
        .filter(*filters)
        .count()
    )
def update_attributes_mapping_tistory_id(session: Session, attributes_mapping: AttributesMapping, tistory_id = int):
    attributes_mapping.tistory_id = tistory_id
    session.add(attributes_mapping)
    session.commit()