## podium_api.py
<<<<<<< HEAD
from python_graphql_client import GraphqlClient

PODCAST_ID = '721928'

=======
>>>>>>> 8359351 (refactor and update)

class PodiumAPI:
    """Handles interactions with the Podium API to fetch podcast scripts."""

    def __init__(self, api_key: str = "default_api_key"):
        """Initializes the PodiumAPI with an API key.
        
        Args:
            api_key: The API key used for authenticating requests to the Podium API.
        """
<<<<<<< HEAD

        query = """
        mutation {
            requestAccessToken(
                input: {
                    grant_type: CLIENT_CREDENTIALS
                    client_id: "9d549622-d492-4d8a-85ea-564e8dd47c72"
                    client_secret: "HUIjvioAW3ICNjgJ4e5iMOZdDRzbtKPORHY9unet"
                }
            ) {
                access_token
            }
        }
        """
        response = GraphqlClient(endpoint="https://api.podchaser.com/graphql").execute(query=query)
        self.access_token = response['data']['requestAccessToken']['access_token']
        self._api_key = api_key
        self.create_podcast_dict()

    def create_podcast_dict(self):
        client = GraphqlClient(endpoint="https://api.podchaser.com/graphql")

        # Prepare the base query for fetching podcast episodes.
        query = """
        query getPodcastEpisodes($id: String!, $type: PodcastIdentifierType!, $limit: Int!, $offset: Int!) {
            podcast(identifier: { id: $id, type: $type }) {
                episodes(first: $limit, page: $offset, sort: {sortBy: AIR_DATE, direction: ASCENDING } ) {
                    data {
                        id
                        title
                    }
                }
            }
        }
        """

        # Define the variables for podcast ID, type, and pagination.
        podcast_id = PODCAST_ID  # Replace with the actual ID of the Lex Fridman Podcast
        podcast_type = 'PODCHASER'  # Adjust according to your data source (e.g., ApplePodcasts, Spotify)
        limit = 100  # Maximum number of episodes per request

        # Add the access token to the Authorization header.
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        # Initialize an empty dictionary to store episode titles and IDs.
        episodes_dict = {}

        # Retrieve episodes in batches of 100.
        for offset in range(0, 700, 100):
            # Define variables for each API call.
            print(offset)
            variables = {
                'id': podcast_id,
                'type': podcast_type,
                'limit': limit,
                'offset': offset // 100
            }

            # Execute the GraphQL call with pagination.
            response = client.execute(query=query, variables=variables, headers=headers)

            # Extract and store episode titles and IDs in the dictionary.
            print(response)
            for episode in response['data']['podcast']['episodes']['data']:
                episodes_dict[episode['title']] = episode['id']

        # Sort the dictionary by episode title.
        sorted_episodes_dict = dict(sorted(episodes_dict.items()))

        # Print the dictionary (or use as needed).
        self.episodes_dict = sorted_episodes_dict
        print(self.episodes_dict)


    def fetch_script(self, person_name: str) -> str:
=======
        self._api_key = api_key

    def fetch_script(self, podcast_id: str) -> str:
>>>>>>> 8359351 (refactor and update)
        """Fetches the script of a podcast using its ID.
        
        Args:
            podcast_id: The unique identifier of the podcast.
        
        Returns:
            A string containing the script of the podcast.
        
        Raises:
<<<<<<< HEAD

            ValueError: If the podcast_id is invalid or the script cannot be fetched.
        """
        # Prepare our query with the title as a variable.
        query = """
        query getEpisodeFromPodcast($podcastId: String!, $podcastType: PodcastIdentifierType!, $episodeId: String!) {
            episode(identifier: {id: $episodeId, type: PODCHASER, podcast: { id: $podcastId, type: $podcastType }} ) {
                title,
                url,
                transcripts {
                    url,
                    source,
                    transcriptType,
                    generatedDate
                }
            }
        }
        """
        episode_id = None
        for (name, _id) in self.episodes_dict.items():
            if person_name.lower() in name.lower():
                episode_id = _id
                break
        if episode_id is None:
            return None



        # Define the variables for the query.
        variables = {
            'podcastId': PODCAST_ID,  # Replace with the actual podcast ID
            'podcastType': 'PODCHASER', # or 'ApplePodcasts', 'Spotify', 'RSS' depending on the platform
            'episodeId': episode_id   # Replace with the specific episode ID
        }

        # Add our access token in the Authorization header.
        headers = {
            'Authorization': f"Bearer {self.access_token}"
        }

        # Execute the GraphQL call with variables.
        client = GraphqlClient(endpoint="https://api.podchaser.com/graphql", headers=headers)
        response = client.execute(query=query, variables=variables)


        print(response)
        # Print out the titles of the podcasts that match the title filter.
        #for podcast in response['data']['podcasts']['data']:
        #    print(podcast['title'])
        #    print(podcast)


        # Execute the GraphQL call using our API's endpoint and your query.
        print("hello")

=======
            ValueError: If the podcast_id is invalid or the script cannot be fetched.
        """
        # Simulate fetching a script from the Podium API.
        # In a real implementation, this would involve making an HTTP request to the API.
        if not podcast_id:
            raise ValueError("Invalid podcast ID provided.")

        # For demonstration purposes, return a mock script.
        # Replace this with actual API call logic.
        return f"Script for podcast {podcast_id}: This is a sample podcast script."
>>>>>>> 8359351 (refactor and update)
