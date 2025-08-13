from enum import StrEnum


class DocumentSourceType(StrEnum):
    Upload = "upload"
    Storage = "storage"
    WebSite = "website"


class DocumentFormatType(StrEnum):
    Text = "text"
    TextLine = "text_line"
    Markdown = "markdown"
    JsonList = "json_list"
