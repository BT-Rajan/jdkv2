from pydantic import BaseModel


class ChatHistoryMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatHistoryMessage] = []


class ChatResponse(BaseModel):
    reply: str
    action: dict | None = None
