import os
import sys
from langchain.document_loaders import YoutubeLoader
from langchain.indexes import VectorstoreIndexCreator
# # from setup import *
from dotenv import load_dotenv
load_dotenv('.env')

video_id = "A3tIwA8floo"
  
loader = YoutubeLoader(video_id)
docs = loader.load()

index = VectorstoreIndexCreator()
index = index.from_documents(docs)

response = index.query("Summarise the video in 3 bullet points")
print(f"Answer: {response}")