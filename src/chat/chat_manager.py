"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRIMAX AI - Chat Manager                                   ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  WATERMARK: PRIMAX-AI-CHAT-MANAGER-BSP-2025                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Message:
    """Chat message"""

    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    """Chat session with context memory"""

    session_id: str
    messages: List[Message] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to session"""
        msg = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        self.last_active = datetime.now().isoformat()
        return msg

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get message history"""
        messages = self.messages[-limit:] if limit else self.messages
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "metadata": msg.metadata,
            }
            for msg in messages
        ]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "message_count": len(self.messages),
            "context": self.context,
            "messages": self.get_history(),
        }


class ChatManager:
    """Manage chat sessions and context"""

    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.max_sessions = 100  # Limit for free tier
        self.max_messages_per_session = 100

    def create_session(self, context: Optional[Dict] = None) -> ChatSession:
        """Create new chat session"""
        session_id = str(uuid.uuid4())
        session = ChatSession(session_id=session_id, context=context or {})

        # Cleanup old sessions if needed
        if len(self.sessions) >= self.max_sessions:
            self._cleanup_old_sessions()

        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get existing session"""
        return self.sessions.get(session_id)

    def add_message(
        self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None
    ) -> Optional[Message]:
        """Add message to session"""
        session = self.get_session(session_id)
        if not session:
            return None

        # Limit messages per session
        if len(session.messages) >= self.max_messages_per_session:
            # Remove oldest messages
            session.messages = session.messages[-(self.max_messages_per_session - 1) :]

        return session.add_message(role, content, metadata)

    def process_message(
        self, session_id: str, user_message: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response

        This is where LLM integration would go.
        For now, returns a placeholder response.
        """
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(context)
            session_id = session.session_id

        # Add user message
        self.add_message(session_id, "user", user_message)

        # Update context if provided
        if context:
            session.context.update(context)

        # Generate response (placeholder - would integrate LLM here)
        response = self._generate_response(session, user_message)

        # Add assistant response
        self.add_message(session_id, "assistant", response)

        return {
            "session_id": session_id,
            "response": response,
            "context": session.context,
            "message_count": len(session.messages),
        }

    def _generate_response(self, session: ChatSession, user_message: str) -> str:
        """
        Generate response based on user message

        TODO: Integrate with LLM (Groq, Claude, or local model)
        """
        message_lower = user_message.lower()

        # Simple intent detection
        if any(
            word in message_lower for word in ["analyze", "scan", "repo", "repository"]
        ):
            return (
                "I can help you analyze your repositories! "
                "Use the `/api/v1/analyze-repos` endpoint to scan specific repos, "
                "or `/api/v1/scan-organization` to analyze your entire Baker Street organization."
            )

        elif any(
            word in message_lower
            for word in ["help", "what can you do", "capabilities"]
        ):
            return (
                "I'm PRIMAX AI, your autonomous DevOps agent! I can:\n"
                "• Analyze repository structures and code\n"
                "• Scan your entire GitHub organization\n"
                "• Generate code with proper watermarks\n"
                "• Analyze system resilience using graph theory\n"
                "• Predict scaling patterns\n"
                "• Automate DevOps tasks\n\n"
                "What would you like me to help with?"
            )

        elif any(word in message_lower for word in ["status", "health", "how are you"]):
            return (
                f"PRIMAX AI v1.0.0 is operational! 🚀\n"
                f"Watermark: PRIMAX-AI-BSP-2025\n"
                f"Session: {session.session_id[:8]}...\n"
                f"Messages in this session: {len(session.messages)}"
            )

        else:
            return (
                "I'm PRIMAX AI, your neuromorphic DevOps agent. "
                "I can analyze repositories, scan organizations, and help with automation. "
                "What would you like to know? (Try 'help' for capabilities)"
            )

    def _cleanup_old_sessions(self):
        """Remove oldest inactive sessions"""
        if not self.sessions:
            return

        # Sort by last_active and keep newest ones
        sorted_sessions = sorted(
            self.sessions.items(), key=lambda x: x[1].last_active, reverse=True
        )

        # Keep only max_sessions - 10
        keep_count = max(self.max_sessions - 10, 10)
        self.sessions = dict(sorted_sessions[:keep_count])

    def list_sessions(self, limit: int = 10) -> List[Dict]:
        """List recent sessions"""
        sorted_sessions = sorted(
            self.sessions.values(), key=lambda x: x.last_active, reverse=True
        )

        return [
            {
                "session_id": s.session_id,
                "created_at": s.created_at,
                "last_active": s.last_active,
                "message_count": len(s.messages),
            }
            for s in sorted_sessions[:limit]
        ]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
