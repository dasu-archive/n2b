from typing import List, Optional
from pydantic import BaseModel


'''
Request DTO 정의
'''
class CategoryDTO(BaseModel):
    id: int
    name: str
    children: List["CategoryDTO"] = []
    depth: int
    opened: bool
    priority: int
    visibility: int
    parent: int
    viewChannel: Optional[str] = None
    entries: int
    categoryInfo: dict = {}
    isNew: bool
    updatedData: bool

class ModifyCategoryRequestDTO(BaseModel):
    append: List[CategoryDTO] = []
    delete: List[int] = []
    rootLabel: str
    update: List[CategoryDTO] = []


'''
Response DTO 정의
'''
class CategoryInfoDTO(BaseModel):
    liststyle: str
    image: str
    description: str

class CategoryTreeDTO(BaseModel):
    id: int
    name: str
    label: str
    priority: int
    entries: int
    visibility: int
    viewChannel: Optional[str] = None
    children: List["CategoryDTO"] = []
    leaf: bool
    categoryInfo: CategoryInfoDTO



class ModifyCategoryResponseDTO(BaseModel):
    categoryTree: List[CategoryTreeDTO] = []
    inputs: ModifyCategoryRequestDTO = []
    rootLabel: str