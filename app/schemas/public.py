"""Public, aggregate information for the Archdiocese landing page."""

from pydantic import BaseModel


class PublicStatistics(BaseModel):
    deaneries: int
    parishes: int
    active_priests: int
    registered_faithful: int


class PublicDeaneryNode(BaseModel):
    name: str
    parishes: list[str]


class PublicOrganigram(BaseModel):
    name: str
    deaneries: list[PublicDeaneryNode]


class PublicOverview(BaseModel):
    statistics: PublicStatistics
    organigram: PublicOrganigram
