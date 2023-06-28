# cleans the data 

from langchain.chat_models.openai import ChatOpenAI
import tiktoken
from pathlib import Path
from langchain.schema import (
    HumanMessage,
    SystemMessage
)

from tqdm.auto import tqdm
from dotenv import load_dotenv
load_dotenv()

MODEL = "gpt-3.5-turbo"
chat = ChatOpenAI(model_name=MODEL, temperature=0.2,max_tokens=500)

def call_openai_api(chunk):
    messages = [
        SystemMessage(content="Clean the following transcripts of all gramatical mistakes, misplaced words."),
        HumanMessage(content=chunk)
    ]
    response = chat(messages)
    return response.content.strip()

def split_into_chunks(text, n_tokens=300):
    encoding = tiktoken.encoding_for_model(MODEL)
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), n_tokens):
        chunks.append(' '.join(encoding.decode(tokens[i:i + n_tokens])))
    return chunks   

def clean_data(input_file, output_file, delay=0):  # delay in seconds (if you hit a rate limit error)
    with Path(input_file).open("r") as file:
        text = file.read()

    chunks = split_into_chunks(text)
    responses = []
    for chunk in tqdm(chunks):
        responses.append(call_openai_api(chunk))

    with Path(output_file).open('w') as file:
        file.write("\n".join(responses))


if __name__ == "__main__":
    input_file = "youtube.txt"
    output_file = "output.txt" 
    try:
        clean_data(input_file, output_file)
    except KeyboardInterrupt:
        print("[PROGRAM STOPPED]")

