## chat_handler.py

from agent import Agent
from typing import List

class ChatHandler:
    """Handles interactions between users and agents, as well as between agents."""

    def handle_user_interaction(self, user_input: str, agents: List[Agent]) -> str:
        """Processes user input and generates a response from the agents.
        
        Args:
            user_input: The input provided by the user.
            agents: A list of agents available for interaction.
        
        Returns:
            A string representing the response from the agents.
        """
        if not agents:
            return "No agents available to interact with."

        # For simplicity, let's assume the first agent responds to the user input.
        # In a real implementation, this could involve more complex logic to choose an agent.
        agent_response = agents[0].mimic_personality()
        return f"User: {user_input}\nAgent: {agent_response}"

    def handle_agent_interaction(self, agent1: Agent, agent2: Agent) -> str:
        """Facilitates interaction between two agents.
        
        Args:
            agent1: The first agent involved in the interaction.
            agent2: The second agent involved in the interaction.
        
        Returns:
            A string representing the interaction result.
        """
        response1 = agent1.mimic_personality()
        response2 = agent2.mimic_personality()
        return f"Interaction between {agent1._name} and {agent2._name}: {response1} | {response2}"
