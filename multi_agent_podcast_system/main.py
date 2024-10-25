## main.py

from flask import Flask, jsonify, request
from agent_manager import AgentManager
from podium_api import PodiumAPI
from user_interface import UserInterface
from chat_handler import ChatHandler

class Main:
    """Main class to initialize and run the application."""

    def __init__(self):
        """Initializes the Main class with necessary components."""
        self._app = Flask(__name__)
        self._agent_manager = AgentManager()
        self._podium_api = PodiumAPI()
        self._user_interface = UserInterface()
        self._chat_handler = ChatHandler()

        # Setup routes for the Flask application
        self._setup_routes()

    def _setup_routes(self):
        """Sets up the routes for the Flask application."""
        @self._app.route('/agents', methods=['GET'])
        def get_agents():
            """Endpoint to get the list of agents."""
            agents = self._agent_manager.get_agents()
            agent_names = [agent._name for agent in agents]
            return jsonify(agent_names)

        @self._app.route('/create_agent', methods=['POST'])
        def create_agent():
            """Endpoint to create a new agent."""
            data = request.json
            name = data.get('name')
            podcast_id = data.get('podcast_id')
            if not name or not podcast_id:
                return jsonify({"error": "Name and podcast_id are required"}), 400

            try:
                script = self._podium_api.fetch_script(podcast_id)
                agent = self._agent_manager.create_agent(name, script)
                return jsonify({"message": f"Agent {agent._name} created successfully"}), 201
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        @self._app.route('/interact_agents', methods=['POST'])
        def interact_agents():
            """Endpoint to facilitate interaction between two agents."""
            data = request.json
            agent1_name = data.get('agent1')
            agent2_name = data.get('agent2')
            agents = self._agent_manager.get_agents()
            agent1 = next((agent for agent in agents if agent._name == agent1_name), None)
            agent2 = next((agent for agent in agents if agent._name == agent2_name), None)

            if not agent1 or not agent2:
                return jsonify({"error": "Both agents must exist"}), 400

            interaction_result = self._agent_manager.interact(agent1, agent2)
            return jsonify({"interaction": interaction_result})

    def run(self):
        """Runs the Flask application."""
        self._app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main_app = Main()
    main_app.run()
