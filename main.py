#!/usr/bin/env python3
# -*- coding:utf-8 -*-


""" imports """
from youtube_to_txt import get_transcript_from_ytchannel
from clean_data import clean_data

import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm

from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from langchain.vectorstores import Pinecone

from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import RetrievalQA

from langchain.agents import Tool
from langchain.agents import initialize_agent





""" env """
import os
from dotenv import load_dotenv
load_dotenv()


""" fetching transcripts from the youtube channel """
API_KEY = os.getenv('Y2_API_KEY')
CHANNEL_ID = "UCdEF3_EFTu78zA7u8JMTk3A"
try:
    get_transcript_from_ytchannel(
        api_key=API_KEY,
        channel_id=CHANNEL_ID,
        no_of_videos=50, 
        output_file='data.txt'
    )
except KeyboardInterrupt:
    print("[PROGRAM STOPPED]")
    exit()


""" clean the data fetched """
try:
    clean_data(
        input_file='data.txt',
        output_file='clean_data.txt'
    )
except KeyboardInterrupt:
    print("[PROGRAM STOPPED]")
    exit()


""" Building the Knowledge Base """
with Path('clean_data.txt').open('r') as file:
    lines = file.read().splitlines()
chunks = [' '.join(lines[i:i+5]) for i in range(0, len(lines), 5)] # Group the lines into chunks of 5
data = pd.DataFrame(chunks, columns=['context'])
data['name'] = 'youtube' # Add an index column and a name column
data.drop_duplicates(subset='context', keep='first', inplace=True)
# print(data)


""" Initialize the Embedding Model and Vector DB """
embed = OpenAIEmbeddings(
    model='text-embedding-ada-002',
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

index_name = 'youtube-chatbot-agent'
pinecone.init(
    api_key=os.getenv('PINECONE_API_KEY'),
    environment=os.getenv('PINECONE_ENV')
)

if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        metric='dotproduct',
        dimension=1536  # 1536 dim of text-embedding-ada-002
    )

index = pinecone.GRPCIndex(index_name)
index.describe_index_stats()


""" Indexing """
data = data.reset_index(drop=True)
data = data.reset_index()
batch_size = 100

for i in tqdm(range(0, len(data), batch_size)):
    i_end = min(len(data), i+batch_size)
    batch = data.iloc[i:i_end]
    metadatas = [
        {
            'text': record[0],  # 'text' will contain the same data as 'context'
            'name': record[1]
        } for record in batch.itertuples(index=False)
    ]
    
    documents = batch['context'].tolist()
    embeds = embed.embed_documents(documents)
    ids = batch['index'].astype(str).tolist()
    index.upsert(vectors=list(zip(ids, embeds, metadatas))) # add everything to pinecone

index = pinecone.Index(index_name)
vectorstore = Pinecone(index, embed.embed_query, "text")
     

""" Initializing the Conversational Agent """
query = "Tell me what do you know?"
vectorstore.similarity_search(
    query,  
    k=3
)

llm = ChatOpenAI(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    model_name='gpt-3.5-turbo',
    temperature=0.0
)

conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    return_messages=True
)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

qa.run(query)

tools = [
    Tool(
        name='Knowledge Base',
        func=qa.run,
        description=(
            'use this tool for every query to get '
            'more information and stories on the topic'
        )
    )
]

agent = initialize_agent(
    agent='chat-conversational-react-description',
    tools=tools,
    llm=llm,
    verbose=False,
    max_iterations=3,
    early_stopping_method='generate',
    memory=conversational_memory
)

agent.agent.llm_chain.prompt = agent.agent.create_prompt(
    system_message="You are y2LLM. Answer the user's questions.",
    tools=tools
)


# I/O
try:
    print('\n')
    while True:
        inp = input("\033[0;39m[ ] [YOU] ")
        output = agent(inp)['output']
        print(f"\033[0;32m[*] [y2LLM] {output}")
except KeyboardInterrupt:
    print("[PROGRAM STOPPED]")


""" Once finished, delete the Pinecone index to save resources """
# pinecone.delete_index(index_name)


