# -*- coding: utf-8 -*-
"""🐫 CAMEL RAG Cookbook.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1sTJ0x_MYRGA76KCg_3I00wj4RL3D2Twp

# 🐫 CAMEL RAG Cookbook

You can also check this cookbook in colab [here](https://colab.research.google.com/drive/1sTJ0x_MYRGA76KCg_3I00wj4RL3D2Twp?usp=sharing)

## Overview

In this notebook, we show the useage of CAMEL Retrieve Module in both customized way and auto way. We will also show how to combine `AutoRetriever` with `ChatAgent`, and further combine `AutoRetriever` with `RolePlaying` by using `Function Calling`.

4 main parts included:

- Customized RAG

- Auto RAG

- Single Agent with Auto RAG

- Role-playing with Auto RAG

### Installation

Ensure you have CAMEL AI installed in your Python environment:
"""

"""## Load Data
Let's first load the CAMEL paper from https://arxiv.org/pdf/2303.17760.pdf. This will be our local example data.


"""

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

"""## 3. Single Agent with Auto RAG
In this section we will show how to combine the `AutoRetriever` with one `ChatAgent`.

Let's set an agent function, in this function we can get the response by providing a query to this agent.
"""

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.types import RoleType
from camel.retrievers import AutoRetriever
from camel.types import StorageType

def single_agent(query: str, name: str) ->str :
    # Set agent role to mimic an individual in a podcast episode using past interview transcripts
    assistant_sys_msg = f"You are now mimicking {name}, a guest from previous podcast episodes. Use the provided transcripts to respond as they would, incorporating their unique style and perspective."

    # Add auto retriever
    auto_retriever = AutoRetriever(
        vector_storage_local_path="local_data2/",
        storage_type=StorageType.QDRANT,
        embedding_model=embedding_instance)

    retrieved_info = auto_retriever.run_vector_retriever(
        query=query,
        contents=glob.glob(f"local_data/{name}*"),
        top_k=1,
        return_detailed_info=False,
        similarity_threshold=0.5
    )

    # Pass the retrieved infomation to agent
    user_msg = str(retrieved_info)
    agent = ChatAgent(assistant_sys_msg)

    # Get response
    assistant_response = agent.step(user_msg)
    return assistant_response.msg.content

# print(single_agent("Please summarize the most important things you said in the past episodes", "Elon Musk"))

"""## 4. Role-playing with Auto RAG
In this section we will show how to combine the `RETRIEVAL_FUNCS` with `RolePlaying` by applying `Function Calling`.
"""

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
from camel.models import ModelFactory
from camel.toolkits import FunctionTool

def role_playing_with_rag(
    task_prompt,
    interviewer,
    interviewee,
    model_platform=ModelPlatformType.OPENAI,
    model_type="gpt-4o",
    chat_turn_limit=5,
) -> None:
    task_prompt = task_prompt
    
    def make_tool(name):
        ar = AutoRetriever(
            vector_storage_local_path="camel/temp_storage",
            storage_type=StorageType.QDRANT,
        )
        def f(*args, **kwds):
            return ar.run_vector_retriever(*args, **kwds, contents=glob.glob(f"local_data/{name}*"))
        return f
    
    tool_lists = []
    for i in range(2):
        name = [interviewer, interviewee][i]
        tool_lists.append([FunctionTool(make_tool(name))])

    role_play_session = RolePlaying(
        user_role_name=interviewer,
        assistant_role_name=interviewee,
        user_agent_kwargs=dict(
            model=ModelFactory.create(
                model_platform=model_platform,
                model_type=model_type,
                # model_config_dict=SambaCloudAPIConfig(max_tokens=8192).as_dict(),
                # url="https://api.sambanovacloud.com/v1"
            ),
            tools=tool_lists[0],
        ),
        assistant_agent_kwargs=dict(
            model=ModelFactory.create(
                model_platform=model_platform,
                model_type=model_type,
                # model_config_dict=SambaCloudAPIConfig(max_tokens=8192).as_dict(),
                # url="https://api.sambanovacloud.com/v1"
            ),
            tools=tool_lists[1],
        ),
        task_prompt=task_prompt,
        with_task_specify=False,
    )

    print(
        Fore.GREEN
        + f"AI Assistant sys message:\n{role_play_session.assistant_sys_msg}\n"
    )
    print(
        Fore.BLUE + f"AI User sys message:\n{role_play_session.user_sys_msg}\n"
    )

    print(Fore.YELLOW + f"Original task prompt:\n{task_prompt}\n")
    print(
        Fore.CYAN
        + "Specified task prompt:"
        + f"\n{role_play_session.specified_task_prompt}\n"
    )
    print(Fore.RED + f"Final task prompt:\n{role_play_session.task_prompt}\n")

    n = 0
    input_msg = role_play_session.init_chat()
    while n < chat_turn_limit:
        n += 1
        assistant_response, user_response = role_play_session.step(input_msg)

        if assistant_response.terminated:
            print(
                Fore.GREEN
                + (
                    "AI Assistant terminated. Reason: "
                    f"{assistant_response.info['termination_reasons']}."
                )
            )
            break
        if user_response.terminated:
            print(
                Fore.GREEN
                + (
                    "AI User terminated. "
                    f"Reason: {user_response.info['termination_reasons']}."
                )
            )
            break

        # Print output from the user
        print_text_animated(
            Fore.BLUE + f"AI User:\n\n{user_response.msg.content}\n"
        )

        # Print output from the assistant, including any function
        # execution information
        print_text_animated(Fore.GREEN + "AI Assistant:")
        tool_calls: List[FunctionCallingRecord] = [
            FunctionCallingRecord(**call.as_dict())
            for call in assistant_response.info['tool_calls']
        ]
        for func_record in tool_calls:
            print_text_animated(f"{func_record}")
        print_text_animated(f"{assistant_response.msg.content}\n")

        if "CAMEL_TASK_DONE" in user_response.msg.content:
            break

        input_msg = assistant_response.msg

"""Run the role-playing with defined retriever function:"""

role_playing_with_rag(
    task_prompt = """Conduct a podcast episode discussion using past podcast transcripts. Each agent should take on a specific role based on their unique perspectives and styles as reflected in the transcripts. Engage in a lively conversation, sharing insights and experiences related to the topics discussed in the previous episodes.""",
    interviewee="Elon Musk",
    interviewer="Bernie Sanders",
)