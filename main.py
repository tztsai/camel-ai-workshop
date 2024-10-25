import os
import glob
import dotenv

dotenv.load_dotenv()
os.makedirs('local_data', exist_ok=True)

"""Import and set the embedding instance:"""

from camel.embeddings import OpenAIEmbedding
from camel.types import EmbeddingModelType

embedding_instance = OpenAIEmbedding(model_type=EmbeddingModelType.TEXT_EMBEDDING_3_LARGE)

"""Import and set the vector storage instance:"""

from camel.storages import QdrantStorage

storage_instance = QdrantStorage(
    vector_dim=embedding_instance.get_output_dim(),
    path="local_data",
    collection_name="podcast",
)

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.types import RoleType
from camel.retrievers import AutoRetriever
from camel.types import StorageType

from typing import List
from colorama import Fore
from functools import partial

from camel.agents.chat_agent import FunctionCallingRecord
from camel.configs import ChatGPTConfig, SambaCloudAPIConfig
from camel.toolkits import (
    MathToolkit,
    RetrievalToolkit,
)
from camel.societies import RolePlaying
from camel.types import ModelType, ModelPlatformType
from camel.utils import print_text_animated
from camel.models import ModelFactory, MistralModel
from camel.toolkits import FunctionTool

from camel.memories import (
    ChatHistoryBlock,
    LongtermAgentMemory,
    MemoryRecord,
    ScoreBasedContextCreator,
    VectorDBBlock,
)
from camel.messages import BaseMessage
from camel.types import ModelType, OpenAIBackendRole
from camel.utils import OpenAITokenCounter

def load_memory(docs):
    # Initialize the memory
    memory = LongtermAgentMemory(
        context_creator=ScoreBasedContextCreator(
            token_counter=OpenAITokenCounter(ModelType.GPT_4O_MINI),
            token_limit=4096,
        ),
        chat_history_block=ChatHistoryBlock(),
        vector_db_block=VectorDBBlock(),
    )

    # Create and write new records
    records = [
        MemoryRecord(
            message=BaseMessage.make_assistant_message(
                role_name="Agent",
                content=open(doc).read(),
            ),
            role_at_backend=OpenAIBackendRole.ASSISTANT,
        ) for doc in docs
    ]
    memory.write_records(records)
    return memory


def role_playing_with_rag(
    task_prompt,
    interviewer,
    interviewee,
    model_platform=ModelPlatformType.OPENAI,
    model_type="gpt-4o-mini",
    chat_turn_limit=5,
) -> None:
    task_prompt = task_prompt
    
    def make_tool(name):
        ar = AutoRetriever(
            vector_storage_local_path="camel/temp_storage",
            storage_type=StorageType.QDRANT,
        )
        def f(*args, **kwds):
            return ar.run_vector_retriever(*args, **kwds, contents=glob.glob(f"local_data/*"))
        return FunctionTool(f)
    
    tool_lists = []
    for i in range(2):
        name = [interviewer, interviewee][i]
        tool_lists.append([make_tool(name)])

    society = RolePlaying(
        user_role_name=interviewer,
        assistant_role_name=interviewee,
        user_agent_kwargs=dict(
            model=ModelFactory.create(
                model_platform=model_platform,
                model_type=model_type,
            ),
            tools=tool_lists[0],
        ),
        assistant_agent_kwargs=dict(
            model=ModelFactory.create(
                model_platform=model_platform,
                model_type=model_type,
            ),
            tools=tool_lists[1],
        ),
        task_prompt=task_prompt,
        with_task_specify=False,
    )
    society.user_agent.memory = load_memory(glob.glob(f"local_data/{interviewer}*"))
    society.assistant_agent.memory = load_memory(glob.glob(f"local_data/{interviewee}*"))

    """### Step 3: Solving Tasks with Your Society
    Hold your bytes. Prior to our travel, let's define a small helper function.
    """

    def is_terminated(response):
        """
        Give alerts when the session shuold be terminated.
        """
        if response.terminated:
            role = response.msg.role_type.name
            reason = response.info['termination_reasons']
            print(f'AI {role} terminated due to {reason}')

        return response.terminated

    """Time to chart our course – writing a simple loop for our society to proceed:"""

    def run(society, round_limit: int=10):

        # Get the initial message from the ai assistant to the ai user
        input_msg = society.init_chat()

        # Starting the interactive session
        for _ in range(round_limit):

            # Get the both responses for this round
            assistant_response, user_response = society.step(input_msg)

            # Check the termination condition
            if is_terminated(assistant_response) or is_terminated(user_response):
                break

            # Get the results
            print(f'[AI User] {user_response.msg.content}.\n')
            # Check if the task is end
            if 'CAMEL_TASK_DONE' in user_response.msg.content:
                break
            print(f'[AI Assistant] {assistant_response.msg.content}.\n')

            # Get the input message for the next round
            input_msg = assistant_response.msg

        return None

    run(society)

"""Run the role-playing with defined retriever function:"""

role_playing_with_rag(
    task_prompt = """Conduct a podcast episode discussion using past podcast transcripts. Each agent should take on a specific role based on their unique perspectives and styles as reflected in the transcripts. Engage in a lively conversation, sharing insights and experiences related to the topics discussed in the previous episodes.""",
    interviewee="Elon",
    interviewer="Bernie",
)