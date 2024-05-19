from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import os

import boto3
from django.conf import settings
from botocore.exceptions import ClientError

from pinecone import Pinecone, ServerlessSpec
from langchain.embeddings import OpenAIEmbeddings

# Initialize Pinecone
pc = Pinecone(
    api_key=settings.PINECONE_API_KEY
)

# Create an index if it doesn't exist
index_name = 'classnotes'
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  # Assuming 768 is the embedding dimension
        metric='cosine',  # Use appropriate metric (euclidean, cosine, etc.)
        spec=ServerlessSpec(
            cloud='aws',
            region=settings.PINECONE_ENVIRONMENT
        )
    )

def get_index():
    return pc.Index(index_name)


cognito_client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)


# Example: Specify the model name explicitly
def store_embeddings(user_id, text_chunks):
    index = get_index()
    namespace = f'user-{user_id}'
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')  # Specify the model here
    vectors = [(f'vec-{i}', embedding, {'text': text_chunks[i]}) for i, embedding in enumerate(embeddings.embed_documents(text_chunks))]
    index.upsert(vectors=vectors, namespace=namespace)

def query_embeddings(user_id, query, top_k=5):
    index = get_index()
    namespace = f'user-{user_id}'
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')
    query_embedding = embeddings.embed_query(query)  # Ensure this returns a valid vector
    # print(query_embedding)
    response = index.query(vector=query_embedding, top_k=top_k, namespace=namespace)  # Ensure 'queries' is a list
    print(response)
    return response

def register_user(username, password, email, phone_number):
    try:
        response = cognito_client.sign_up(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'phone_number', 'Value': phone_number},
            ],
        )
        return response
    except ClientError as e:
        raise e

def confirm_registration(username, confirmation_code):
    try:
        response = cognito_client.confirm_sign_up(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            Username=username,
            ConfirmationCode=confirmation_code,
        )
        return response
    except ClientError as e:
        raise e

def login_user(username, password):
    try:
        response = cognito_client.initiate_auth(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
            },
        )
        return response
    except ClientError as e:
        raise e

def logout_user(access_token):
    try:
        response = cognito_client.global_sign_out(
            AccessToken=access_token,
        )
        return response
    except ClientError as e:
        raise e


VECTORSTORE_PATH = "vectorstore.faiss"

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks, api_key):
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)
    return vectorstore

def load_vectorstore(api_key):
    if os.path.exists(VECTORSTORE_PATH):
        vectorstore = FAISS.load_local(VECTORSTORE_PATH, embeddings=OpenAIEmbeddings(openai_api_key=api_key))
        return vectorstore
    else:
        return None

def get_conversation_chain(vectorstore, api_key):
    llm = ChatOpenAI(openai_api_key=api_key)
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

