"""
CogniMap Protocol - Communication and data standards.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
import json


class ProtocolVersion(Enum):
    """CogniMap protocol versions."""
    V1_0 = "1.0.0"
    V1_1 = "1.1.0"
    CURRENT = V1_0


class ComponentType(Enum):
    """Types of components in the architecture."""
    AGENT = "agent"
    TOOL = "tool"
    SERVICE = "service"
    MODEL = "model"
    CONTROLLER = "controller"
    REPOSITORY = "repository"
    UTILITY = "utility"
    TEST = "test"
    CONFIGURATION = "configuration"
    PROTOCOL = "protocol"
    UNKNOWN = "unknown"


class RelationshipType(Enum):
    """Types of relationships between components."""
    IMPORTS = "imports"
    EXPORTS = "exports"
    USES = "uses"
    IMPLEMENTS = "implements"
    EXTENDS = "extends"
    DEPENDS_ON = "depends_on"
    CALLS = "calls"
    PUBLISHES_TO = "publishes_to"
    SUBSCRIBES_TO = "subscribes_to"
    READS_FROM = "reads_from"
    WRITES_TO = "writes_to"
    CONTAINS = "contains"
    SEMANTICALLY_RELATED = "semantically_related"
    DATA_FLOW = "data_flow"
    CONTROL_FLOW = "control_flow"


class ArchitecturalLayer(Enum):
    """Architectural layers in the system."""
    PRESENTATION = "presentation"
    BUSINESS = "business"
    DATA = "data"
    PERSISTENCE = "persistence"
    INFRASTRUCTURE = "infrastructure"
    UTILITY = "utility"
    TESTING = "testing"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class EventType(Enum):
    """Types of events in the CogniMap system."""
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    RELATIONSHIP_DISCOVERED = "relationship_discovered"
    RELATIONSHIP_REMOVED = "relationship_removed"
    ANALYSIS_COMPLETED = "analysis_completed"
    WARNING_DETECTED = "warning_detected"
    PATTERN_DETECTED = "pattern_detected"


class WarningSeverity(Enum):
    """Severity levels for warnings."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CogniMapNode:
    """Represents a node in the CogniMap graph."""
    id: str
    filepath: str
    fingerprint: Dict[str, Any]
    scan_result: Dict[str, Any]
    semantic_analysis: Dict[str, Any]
    component_type: ComponentType
    architectural_layer: ArchitecturalLayer
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'filepath': self.filepath,
            'fingerprint': self.fingerprint,
            'scan_result': self.scan_result,
            'semantic_analysis': self.semantic_analysis,
            'component_type': self.component_type.value,
            'architectural_layer': self.architectural_layer.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CogniMapNode':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            filepath=data['filepath'],
            fingerprint=data['fingerprint'],
            scan_result=data['scan_result'],
            semantic_analysis=data['semantic_analysis'],
            component_type=ComponentType(data['component_type']),
            architectural_layer=ArchitecturalLayer(data['architectural_layer']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )


@dataclass
class CogniMapEdge:
    """Represents an edge/relationship in the CogniMap graph."""
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    strength: float  # 0.0 to 1.0
    verified: bool
    metadata: Dict[str, Any]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relationship_type': self.relationship_type.value,
            'strength': self.strength,
            'verified': self.verified,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CogniMapEdge':
        """Create from dictionary."""
        return cls(
            source_id=data['source_id'],
            target_id=data['target_id'],
            relationship_type=RelationshipType(data['relationship_type']),
            strength=data['strength'],
            verified=data['verified'],
            metadata=data['metadata'],
            created_at=datetime.fromisoformat(data['created_at'])
        )


@dataclass
class CogniMapEvent:
    """Represents an event in the CogniMap system."""
    event_type: EventType
    component_id: str
    timestamp: datetime
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_type': self.event_type.value,
            'component_id': self.component_id,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class CogniMapWarning:
    """Represents a warning in the system."""
    component_id: str
    warning_type: str
    message: str
    severity: WarningSeverity
    suggestion: Optional[str]
    detected_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'component_id': self.component_id,
            'warning_type': self.warning_type,
            'message': self.message,
            'severity': self.severity.value,
            'suggestion': self.suggestion,
            'detected_at': self.detected_at.isoformat()
        }


class CogniMapProtocol:
    """Main protocol handler for CogniMap communication."""
    
    def __init__(self, version: ProtocolVersion = ProtocolVersion.CURRENT):
        self.version = version
        
    def create_fingerprint_message(self, filepath: str, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fingerprint registration message."""
        return {
            'protocol_version': self.version.value,
            'message_type': 'fingerprint_registration',
            'filepath': filepath,
            'fingerprint': fingerprint,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def create_relationship_message(self, source: str, target: str, rel_type: RelationshipType, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a relationship discovery message."""
        return {
            'protocol_version': self.version.value,
            'message_type': 'relationship_discovery',
            'source': source,
            'target': target,
            'relationship_type': rel_type.value,
            'metadata': metadata or {},
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def create_analysis_message(self, filepath: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create an analysis result message."""
        return {
            'protocol_version': self.version.value,
            'message_type': 'analysis_result',
            'filepath': filepath,
            'analysis': analysis,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def create_warning_message(self, warning: CogniMapWarning) -> Dict[str, Any]:
        """Create a warning message."""
        return {
            'protocol_version': self.version.value,
            'message_type': 'warning',
            'warning': warning.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def parse_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate a CogniMap message."""
        # Check protocol version
        msg_version = message.get('protocol_version')
        if msg_version != self.version.value:
            raise ValueError(f"Protocol version mismatch: expected {self.version.value}, got {msg_version}")
        
        # Validate message type
        msg_type = message.get('message_type')
        valid_types = ['fingerprint_registration', 'relationship_discovery', 'analysis_result', 'warning', 'event']
        if msg_type not in valid_types:
            raise ValueError(f"Invalid message type: {msg_type}")
        
        # Validate required fields based on message type
        if msg_type == 'fingerprint_registration':
            required = ['filepath', 'fingerprint']
        elif msg_type == 'relationship_discovery':
            required = ['source', 'target', 'relationship_type']
        elif msg_type == 'analysis_result':
            required = ['filepath', 'analysis']
        elif msg_type == 'warning':
            required = ['warning']
        else:
            required = []
        
        for field in required:
            if field not in message:
                raise ValueError(f"Missing required field: {field}")
        
        return message
    
    def validate_fingerprint(self, fingerprint: Dict[str, Any]) -> bool:
        """Validate a fingerprint structure."""
        required_fields = ['id', 'birth', 'intent', 'semantic_tags', 'version']
        return all(field in fingerprint for field in required_fields)
    
    def validate_relationship(self, relationship: Dict[str, Any]) -> bool:
        """Validate a relationship structure."""
        required_fields = ['source_id', 'target_id', 'relationship_type']
        
        # Check required fields
        if not all(field in relationship for field in required_fields):
            return False
        
        # Check relationship type is valid
        try:
            RelationshipType(relationship['relationship_type'])
            return True
        except ValueError:
            return False
    
    def serialize_node(self, node: CogniMapNode) -> str:
        """Serialize a node to JSON."""
        return json.dumps(node.to_dict(), indent=2)
    
    def deserialize_node(self, data: str) -> CogniMapNode:
        """Deserialize a node from JSON."""
        return CogniMapNode.from_dict(json.loads(data))
    
    def serialize_edge(self, edge: CogniMapEdge) -> str:
        """Serialize an edge to JSON."""
        return json.dumps(edge.to_dict(), indent=2)
    
    def deserialize_edge(self, data: str) -> CogniMapEdge:
        """Deserialize an edge from JSON."""
        return CogniMapEdge.from_dict(json.loads(data))