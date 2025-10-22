from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status"""
    QUEUED = "Queued"
    IN_PROGRESS = "In Progress"
    PROCESSED = "Processed"
    FAILED = "Failed"


class AgentType(str, Enum):
    """Available agent types"""
    ACCOUNTANT = "AccountantAgent"
    TAX = "TaxAgent"
    FORECAST = "ForecastAgent"
    COMPLIANCE = "ComplianceAgent"
    AUDIT = "AuditAgent"
    REPORTER = "ReporterAgent"
    INVESTMENT = "InvestmentAgent"
    COMMS = "CommsAgent"


class UploadMetadata(BaseModel):
    """Metadata for document upload"""
    assigned_agents: List[AgentType] = Field(default_factory=list)
    doctype: str = Field(default="Financial Document")
    country: str = Field(default="CA")
    province: Optional[str] = None
    year: Optional[int] = None
    tags: List[str] = Field(default_factory=list)


class UploadResponse(BaseModel):
    """Response after document upload"""
    message: str
    document_id: str
    filename: str
    status: DocumentStatus
    processing_time: Optional[float] = None


class QueryRequest(BaseModel):
    """Request for RAG query"""
    query: str = Field(..., min_length=1, max_length=2000)
    document_name: Optional[str] = None
    agent: Optional[AgentType] = None
    namespace: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=50)
    use_rerank: bool = True


class ToolCall(BaseModel):
    """Tool call information"""
    tool_name: str
    input: Dict[str, Any]
    output: Optional[str] = None


class QueryResponse(BaseModel):
    """Response from RAG query"""
    agent: str
    response: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    tool_calls: List[ToolCall] = Field(default_factory=list)
    processing_time: float
    tokens_used: Optional[int] = None


class Document(BaseModel):
    """Document metadata"""
    id: str
    name: str
    status: DocumentStatus
    uploaded: datetime
    assigned_agents: List[AgentType]
    tags: List[str]
    doctype: str
    country: str
    province: Optional[str] = None
    year: Optional[int] = None
    size_bytes: int
    chunk_count: Optional[int] = None
    sha256: str


class DocumentListResponse(BaseModel):
    """Response for document list"""
    documents: List[Document]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    services: Dict[str, str]
    timestamp: datetime


class AgentStatus(BaseModel):
    """Agent status information"""
    name: AgentType
    status: str
    assigned_documents: int
    last_query: Optional[datetime] = None
    total_queries: int


class AgentListResponse(BaseModel):
    """Response for agent list"""
    agents: List[AgentStatus]
