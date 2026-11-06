from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message text or transcribed speech")
    audio_url: Optional[str] = Field(None, description="Optional audio file URL or reference")
    language_code: Optional[str] = Field(None, description="Optional ISO language code, e.g. 'mr-IN', 'hi-IN'")

class ChatResponse(BaseModel):
    session_id: str
    domain: str
    reply: str
    is_complete: bool = False
    escalation_triggered: bool = False
    escalation_reason: Optional[str] = None
    missing_variables: List[str] = Field(default_factory=list)
    facts: Dict[str, Any] = Field(default_factory=dict)
    legal_notice_draft: Optional[str] = None

class AudioChatResponse(BaseModel):
    session_id: str
    domain: str
    user_transcription: str
    detected_language: str
    reply: str
    audio_base64: Optional[str] = None
    is_complete: bool = False
    escalation_triggered: bool = False
    escalation_reason: Optional[str] = None
    missing_variables: List[str] = Field(default_factory=list)
    facts: Dict[str, Any] = Field(default_factory=dict)
    legal_notice_draft: Optional[str] = None

class TriageResult(BaseModel):
    domain: str = Field(..., description="One of: 'rental_deposit', 'unpaid_salary', or 'out_of_scope'")
    confidence: float = Field(default=1.0)
    explanation: str = Field(default="")
    is_escalation: bool = Field(default=False)
    escalation_reason: Optional[str] = None
