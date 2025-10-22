from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class AgentConfig(Base):
    """Agent configuration stored in database"""
    __tablename__ = "agent_configs"
    
    id = Column(String, primary_key=True)  # e.g., "AccountantAgent"
    name = Column(String, nullable=False)  # Display name
    role = Column(String, nullable=False)
    goal = Column(Text, nullable=False)
    backstory = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=True)  # Custom system prompt
    namespace = Column(String, nullable=False, default="default")
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_custom = Column(Boolean, default=False)  # True if user-created
    is_remote = Column(Boolean, default=False)  # True if SSH remote agent
    icon = Column(String, default="🤖")
    color = Column(String, default="#64ffda")
    
    # SSH Configuration (for remote agents)
    ssh_host = Column(String, nullable=True)  # e.g., "192.168.1.10"
    ssh_port = Column(Integer, default=22)
    ssh_username = Column(String, nullable=True)
    ssh_key_path = Column(String, nullable=True)  # Path to private key
    ssh_password = Column(String, nullable=True)  # Encrypted password (fallback)
    ssh_endpoint = Column(String, default="/process")  # API endpoint on remote agent
    
    # Metadata
    tools = Column(JSON, default=list)  # List of tool names
    metadata = Column(JSON, default=dict)  # Additional config
    
    # Statistics
    query_count = Column(Integer, default=0)
    last_query_time = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "system_prompt": self.system_prompt,
            "namespace": self.namespace,
            "is_active": self.is_active,
            "is_custom": self.is_custom,
            "is_remote": self.is_remote,
            "icon": self.icon,
            "color": self.color,
            "ssh_host": self.ssh_host,
            "ssh_port": self.ssh_port,
            "ssh_username": self.ssh_username,
            "ssh_endpoint": self.ssh_endpoint,
            "tools": self.tools,
            "metadata": self.metadata,
            "query_count": self.query_count,
            "last_query_time": self.last_query_time.isoformat() if self.last_query_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class DocumentMetadata(Base):
    """Document metadata stored in database"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, default="Queued")
    uploaded = Column(DateTime, default=func.now())
    
    # Assignment
    assigned_agents = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    
    # Document info
    doctype = Column(String, default="Financial Document")
    country = Column(String, default="CA")
    province = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    
    # File info
    size_bytes = Column(Integer, default=0)
    chunk_count = Column(Integer, nullable=True)
    sha256 = Column(String, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "uploaded": self.uploaded.isoformat() if self.uploaded else None,
            "assigned_agents": self.assigned_agents,
            "tags": self.tags,
            "doctype": self.doctype,
            "country": self.country,
            "province": self.province,
            "year": self.year,
            "size_bytes": self.size_bytes,
            "chunk_count": self.chunk_count,
            "sha256": self.sha256
        }
