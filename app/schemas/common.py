from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class TestCaseIdCollectionRequest(BaseModel):
    test_case_ids: List[int] = Field(default_factory=list, min_length=1, max_length=200)

    @field_validator("test_case_ids")
    @classmethod
    def normalize_ids(cls, value: List[int]) -> List[int]:
        normalized: List[int] = []
        seen: set[int] = set()
        for item in value:
            if item <= 0:
                raise ValueError("test_case_ids must contain positive integers")
            if item in seen:
                continue
            seen.add(item)
            normalized.append(item)
        if not normalized:
            raise ValueError("test_case_ids must not be empty")
        return normalized


class BulkDeleteResponse(BaseModel):
    message: str
    deleted_count: int
    deleted_ids: List[int]

