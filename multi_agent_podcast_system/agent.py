## agent.py

class Agent:
    """Represents an agent that mimics a podcast personality."""
    
    def __init__(self, name: str, script: str):
        """Initializes an Agent with a name and a script.
        
        Args:
            name: The name of the agent.
            script: The script that the agent will use to mimic a personality.
        """
        self._name = name
        self._script = script

    def mimic_personality(self) -> str:
        """Mimics the personality of the agent based on the script.
        
        Returns:
            A string that represents the agent's response.
        """
        # For simplicity, let's assume the agent just returns a part of the script.
        # In a real implementation, this could involve more complex logic.
        return f"{self._name} says: {self._script[:50]}..."  # Return the first 50 characters of the script.
