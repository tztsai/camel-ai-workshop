## agent_manager.py

from typing import List
from agent import Agent

class AgentManager:
    """Manages the creation and interaction of agents."""

    def __init__(self):
        """Initializes the AgentManager with an empty list of agents."""
        self._agents: List[Agent] = []

    def create_agent(self, name: str, script: str) -> Agent:
        """Creates a new agent and adds it to the list of agents.
        
        Args:
            name: The name of the agent.
            script: The script that the agent will use to mimic a personality.
        
        Returns:
            The created Agent object.
        """
        agent = Agent(name, script)
        self._agents.append(agent)
        return agent

    def get_agents(self) -> List[Agent]:
        """Retrieves the list of all agents.
        
        Returns:
            A list of Agent objects.
        """
        return self._agents

    def interact(self, agent1: Agent, agent2: Agent) -> str:
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
