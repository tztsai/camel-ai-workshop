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
import requests

dotenv.load_dotenv()
os.makedirs('local_data', exist_ok=True)

url = "https://arxiv.org/pdf/2303.17760.pdf"
response = requests.get(url)
with open('local_data/camel_paper.pdf', 'wb') as file:
     file.write(response.content)

"""## 1. Customized RAG
In this section we will set our customized RAG pipeline, we will take `VectorRetriever` as an example.
Set embedding model, we will use `OpenAIEmbedding` as the embedding model, so we need to set the `OPENAI_API_KEY` in below.
"""


"""Import and set the embedding instance:"""

from camel.embeddings import OpenAIEmbedding
from camel.types import EmbeddingModelType

embedding_instance = OpenAIEmbedding(model_type=EmbeddingModelType.TEXT_EMBEDDING_3_LARGE)

"""Import and set the vector storage instance:"""

from camel.storages import QdrantStorage

storage_instance = QdrantStorage(
    vector_dim=embedding_instance.get_output_dim(),
    path="local_data",
    collection_name="camel_paper",
)

"""Import and set the retriever instance:"""

from camel.retrievers import VectorRetriever

vector_retriever = VectorRetriever(embedding_model=embedding_instance,
                                   storage=storage_instance)

"""We use integrated `Unstructured Module` to splite the content into small chunks, the content will be splited automacitlly with its `chunk_by_title` function, the max character for each chunk is 500 characters, which is a suitable length for `OpenAIEmbedding`. All the text in the chunks will be embed and stored to the vector storage instance, it will take some time, please wait.."""

vector_retriever.process(
    content="local_data/camel_paper.pdf",
)

"""
Now we can retrieve information from the vector storage by giving a query. By default it will give you back the text content from top 1 chunk with highest Cosine similarity score, and the similarity score should be higher than 0.75 to ensure the retrieved content is relevant to the query. You can also change the `top_k` value and `similarity_threshold` value with your needs.

The returned dictionary list includes:
- similarity score
- content path
- metadata
- text"""

retrieved_info = vector_retriever.query(
    query="To address the challenges of achieving autonomous cooperation, we propose a novel communicative agent framework named role-playing .",
    top_k=1
)
print(retrieved_info)

"""Let's try an irrelevant query:"""

retrieved_info_irrevelant = vector_retriever.query(
    query="Compared with dumpling and rice, which should I take for dinner?",
    top_k=1,
)

print(retrieved_info_irrevelant)

"""## 2. Auto RAG
In this section we will run the `AutoRetriever` with default settings. It uses `OpenAIEmbedding` as default embedding model and `Milvus` as default vector storage.

What you need to do is:
- Set content input paths, which can be local paths or remote urls
- Set remote url and api key for Milvus
- Give a query

The Auto RAG pipeline would create collections for given content input paths, the collection name will be set automaticlly based on the content input path name, if the collection exists, it will do the retrieve directly.
"""

from camel.retrievers import AutoRetriever
from camel.types import StorageType

auto_retriever = AutoRetriever(
        vector_storage_local_path="local_data2/",
        storage_type=StorageType.QDRANT,
        embedding_model=embedding_instance)

retrieved_info = auto_retriever.run_vector_retriever(
    query="If I'm interest in contributing to the CAMEL projec, what should I do?",
    contents=[
        "local_data/camel_paper.pdf",  # example local path
        "https://github.com/camel-ai/camel/wiki/Contributing-Guidlines",  # example remote url
    ],
    top_k=1,
    return_detailed_info=True,
    similarity_threshold=0.5
)

print(retrieved_info)

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

print(single_agent("If I'm interest in contributing to the CAMEL projec, what should I do?"))

"""## 4. Role-playing with Auto RAG
In this section we will show how to combine the `RETRIEVAL_FUNCS` with `RolePlaying` by applying `Function Calling`.

"""

from typing import List
from colorama import Fore

from camel.agents.chat_agent import FunctionCallingRecord
from camel.configs import ChatGPTConfig
from camel.toolkits import (
    MathToolkit,
    RetrievalToolkit,
)
from camel.societies import RolePlaying
from camel.types import ModelType, ModelPlatformType
from camel.utils import print_text_animated
from camel.models import ModelFactory

def role_playing_with_rag(
    task_prompt,
    model_platform=ModelPlatformType.OPENAI,
    model_type=ModelType.GPT_4O_MINI,
    chat_turn_limit=5,
) -> None:
    task_prompt = task_prompt

    tools_list = [
        *MathToolkit().get_tools(),
        *RetrievalToolkit().get_tools(),
    ]


    role_play_session = RolePlaying(
        assistant_role_name="Searcher",
        user_role_name="Professor",
        assistant_agent_kwargs=dict(
            model=ModelFactory.create(
                model_platform=model_platform,
                model_type=model_type,
            ),
            tools=tools_list,
        ),
        user_agent_kwargs=dict(
            model=ModelFactory.create(
                model_platform=model_platform,
                model_type=model_type,
            ),
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

role_playing_with_rag(task_prompt = """If I'm interest in contributing to the CAMEL projec and I encounter some challenges during the setup process, what should I do? You should refer to the content in url https://github.com/camel-ai/camel/wiki/Contributing-Guidlines to answer my question, don't generate the answer by yourself, adjust the similarity threshold to lower value is necessary""")