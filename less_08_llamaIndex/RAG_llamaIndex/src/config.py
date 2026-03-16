import os
from pinecone import Pinecone
from llama_index.core import Settings, StorageContext
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from google.genai.types import EmbedContentConfig    

def init_app_settings():
    
    Settings.llm = GoogleGenAI(
        model="models/gemini-3-flash-preview",
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    Settings.embed_model = GoogleGenAIEmbedding(
        model_name="models/gemini-embedding-001",
        api_key=os.environ.get("GEMINI_API_KEY"),
        embedding_config=EmbedContentConfig(output_dimensionality=768),
    )

    pc = Pinecone(
        api_key=os.environ["PINECONE_API_KEY"],
        ssl_ca_certs="C:\\Users\\User\\Documents\\netfree-ca.crt" 
    )

    pinecone_index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    return vector_store, storage_context, pinecone_index