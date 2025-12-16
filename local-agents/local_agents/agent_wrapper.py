"""Agent wrapper for capturing assistant messages."""

from typing import Any
from strands.hooks import MessageAddedEvent


class AgentWrapper:
    """Wrapper that captures and provides access to assistant messages from agent interactions.
    
    This wrapper intercepts MessageAddedEvent hooks to collect assistant responses,
    allowing retrieval of the last conversation messages in various formats.
    """
    
    def __init__(self, agent: Any) -> None:
        """Initialize wrapper with an agent instance.
        
        Args:
            agent: The agent instance to wrap and monitor for messages.
            
        Raises:
            ValueError: If agent doesn't have 'hooks' attribute.
        """
        if not hasattr(agent, 'hooks'):
            raise ValueError("Agent must have 'hooks' attribute")
        
        self.agent = agent
        self.last_messages: list[str] = []
        self.agent.hooks.add_callback(MessageAddedEvent, self.get_assistant_messages)

    def __call__(self, user_input: str) -> str:
        """Process user input and return assistant messages as string.
        
        Args:
            user_input: The user's input message.
            
        Returns:
            Combined assistant messages from the interaction.
        """
        self.last_messages: list[str] = []
        self.agent(user_input)
        return self.get_last_messages_as_string()

    def get_assistant_messages(self, event: MessageAddedEvent) -> None:
        """Hook callback to capture assistant messages.
        
        Args:
            event: MessageAddedEvent containing the new message.
        """
        if event.message["role"] == "assistant":
            content_text = "".join(block.get("text", "") for block in event.message["content"] if isinstance(block, dict))
            self.last_messages.append(content_text)

    def get_last_messages_as_string(self) -> str:
        """Get all captured messages joined as a single string.
        
        Returns:
            Messages separated by '\n ... \n\n' delimiter.
        """
        return "\n ... \n\n".join(self.last_messages)

    def get_last_messages_as_list(self) -> list[str]:
        """Get all captured messages as a list.
        
        Returns:
            List of individual message strings.
        """
        return self.last_messages

    def get_last_message(self) -> str:
        """Get the most recent captured message.
        
        Returns:
            The last message string, or empty string if none captured.
        """
        return self.last_messages[-1] if self.last_messages else ""