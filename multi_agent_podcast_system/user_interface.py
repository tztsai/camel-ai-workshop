## user_interface.py

from typing import List
from agent import Agent

class UserInterface:
    """Handles user interactions with the system."""

    def display_agents(self, agents: List[Agent]) -> None:
        """Displays a list of available agents to the user.
        
        Args:
            agents: A list of Agent objects to be displayed.
        """
        if not agents:
            print("No agents available.")
            return

        print("Available Agents:")
        for index, agent in enumerate(agents, start=1):
            print(f"{index}. {agent._name}")

    def get_user_input(self) -> str:
        """Prompts the user for input and returns it.
        
        Returns:
            A string containing the user's input.
        """
        user_input = input("Enter your message: ")
        return user_input

    def display_response(self, response: str) -> None:
        """Displays the response from the system to the user.
        
        Args:
            response: The response string to be displayed.
        """
        print("Response from system:")
        print(response)
