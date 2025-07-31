from enum import StrEnum


class DocumentSourceType(StrEnum):
    Upload = "upload"
    Storage = "storage"
    WebSite = "website"
