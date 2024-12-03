import openai
import json
import os
from decouple import config

# Import custom function
from functions.database import get_previous_responses, get_stored_topic, store_documents

# Import vector store embeddings
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from uuid import uuid4

# Ensemble retrieval and filters
import nltk
from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever


# Environment variables
# nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('averaged_perceptron_tagger')
openai.organisation = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")

open_ai_embeddings = AzureOpenAIEmbeddings(azure_endpoint=config('AZURE_OPENAI_ENDPOINT'), 
                                   api_key=config('AZURE_OPENAI_APIKEY'), 
                                   model=config('TEXT_EMBEDDING_MODEL_NAME'),
                                   azure_deployment=config('TEXT_EMBEDDING_DEPLOYMENT_NAME'))

embeddings=HuggingFaceInferenceAPIEmbeddings(
    api_key=config('HUGGING_FACE_ACCESS_TOKEN'),
    model_name='BAAI/bge-base-en-v1.5'
)

# Hugging face embeddings vector store
global loaded_faiss_vs_hf_v3
global documents_json
global documents

# 'C:\\Roydon\\Github\\FYP_Application\\MuteCompanion\\backend\mockdata\\documents.json'
# "C:\\Roydon\\Github\\FYP_Application\\MuteCompanion\\MuteApp\\assets\\mockdata\\Jane\\documents.json"
json_file_path = "C:\\Roydon\\Github\\FYP_V2\\muteApp\\assets\\mockdata\\Jane\\documents.json"

# Open_ai_vector store
#C:\\Roydon\\Github\\FYP_Application\\MuteCompanion\\backend\\vector_store\\vectorstores\\faiss_vs
# "C:\\Roydon\\Github\\FYP_Application\\MuteCompanion\\MuteApp\\assets\\mockdata\\Jane\\faiss_vectorstore_open_ai_Jane"
loaded_faiss_vs = FAISS.load_local("C:\\Roydon\\Github\\FYP_V2\\muteApp\\assets\\mockdata\\Jane\\faiss_vectorstore_open_ai_Jane", embeddings=open_ai_embeddings, allow_dangerous_deserialization=True)

# Initialize variables
#start = 0
#final_response = ""

# Load documents
# json_file_path = 'C:\\Roydon\\Github\\FYP_Application\\MuteCompanion\\backend\mockdata\\documents.json'

# Initiate retrievers
global retriever_vectordb
global keyword_retriever
global ensemble_retriever

def initialize_variables(json_file_path=json_file_path):
    global loaded_faiss_vs_hf_v3
    global documents_json
    global documents

    # Retrievers
    global retriever_vectordb
    global keyword_retriever
    global ensemble_retriever


    # C:\\Roydon\\Github\\FYP_Application\\MuteCompanion\\backend\\vector_store\\vectorstores\\hugging_face\\faiss_vs_hf_v3
    # "C:\\Roydon\Github\\FYP_Application\\MuteCompanion\\MuteApp\\assets\\mockdata\\Jane\\faiss_vectorstore_Jane_V2"
    loaded_faiss_vs_hf_v3 = FAISS.load_local("C:\\Roydon\\Github\\FYP_V2\\muteApp\\assets\\mockdata\\Jane\\faiss_vectorstore_Jane_V2", embeddings=embeddings, allow_dangerous_deserialization=True)
    with open(json_file_path, 'r') as json_file:
        documents_json = json.load(json_file)
    
    # Convert the JSON serializable format back to Document objects
    documents = [
        Document(page_content=doc['page_content'], metadata=doc['metadata'])
        for doc in documents_json
    ]

    print(f"Loaded {len(documents)} documents.")

    # Initialize the retrievers
    retriever_vectordb = loaded_faiss_vs_hf_v3.as_retriever(search_kwargs={"k": 6})
    keyword_retriever = BM25Retriever.from_documents(documents)
    keyword_retriever.k =  3
    ensemble_retriever = EnsembleRetriever(retrievers=[retriever_vectordb,keyword_retriever],
                                        weights=[0.7, 0.3])
    
#--------------------------------------------- Initialize variables ---------------------------------------------

# Initialize variables
initialize_variables()

#--------------------------------------------- Response Generation ---------------------------------------------

# Convert audio to text using open ai whisper
def audio_to_text(audio_file):
    try:
        transcript = openai.audio.transcriptions.create(
            model = "whisper-1", 
            file = audio_file,
            language = "en",)
        text = transcript.text
        return text
    except Exception as e:
        print(e)
        return


def getTopic(meta_content, query):
    # Learning instructions
    instruction = {
        "role": "system",
        "content": meta_content,
    }

    #print("Query is: " + query)

    # Initialize messages
    messages_topic = []

    # Add learn instruction to message array
    messages_topic.append(instruction)

    user_message = {
            "role": "user",
            "content": query
    }

    messages_topic.append(user_message)

    try:
        raw_response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages = messages_topic,
        )
        topic = raw_response.choices[0].message.content

        return topic
    except Exception as e:
        print(e)
        return




# Get chatgpt assistant responses
# message input is the audio input from
# Output: 3 response choices, user message content
def get_response_choice(mute, normal, final_response, message, search, failsafe_retriever = loaded_faiss_vs):
    global start
    #global final_response
    messages = get_previous_responses(getTopic, ensemble_retriever, message, search, failsafe_retriever, mute, normal)
    user_message = {}
  
    user_message = {
        "role": "user",
        "content": f"{mute} says: " + final_response + f"{normal} says: " + message
    }

    messages.append(user_message)
    # print(messages)
    # print("Start is: " + str(start))

    try:
        raw_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages = messages 
        )
        #print(raw_response)
    
        # Split response choices for user to pick
        response_choices = raw_response.choices[0].message.content
        #print("User message is: ", user_message["content"])
        return response_choices, user_message["content"]
    except Exception as e:
        print(e)
        return

# Adds the final response to the final response variable for the next use of query
def add_final_response(response_selected):
    global final_response

    # For now assume user picks first choice
    final_response = response_selected
    print(final_response)

#--------------------------------------------- Regenerate Singular Response And Rank ---------------------------------------------
def rank_and_regenerate(mute, normal, responses, query, scores, badResponse):
    
    # Instruction prompt
    meta_content = f"""
    You are an assistant whom will faciliate the conversation between a mute and a normal person. The mute persons name is {mute} and the normal person is indicated as {normal}.
    You previously generated the following responses:
    {responses}
    For the query of: {query}

    The score of the responses are as follows respectively with a max score of 1 being a good response, 0.5 being neutral and below 0.5 being a bad response:
    {scores}

    You have to generate a response that would replace the {badResponse} using the other responses (above 0.5) as a guide. Use responses with higher scores first (those with score of 1).
    Do not repeat any of the previously generated responses.
    The responses should be what a person would say and should not include actions in a third person view. Your persona would be from the perspective of the mute person.

    For example, 
    If the query is: "Hey Jane, what are you up to?"
    and the responses previously generated were:
    ["Hi Gary, I've been keeping busy with work and some new hobbies.", "Hey Gary, I've been learning how to cook new recipes and exploring different cuisines. It's been a fun and delicious experience!", "Hey Gary, I've been learning gardening, how about you?"]
    and the scores are [0.5, 0, 1] respectively,
    then, the good response is: "Hey Gary, I've been learning gardening, how about you"?
    and the bad response is "Hey Gary, I've been learning how to cook new recipes and exploring different cuisines. It's been a fun and delicious experience!"

    The generated response should not be about cooking and should be about gardening (using the good response as a guide to infer the topic). Do not not repeat any previous responses like "Hi Gary, I've been keeping busy with work and some new hobbies." 
    Do not explain reasoning and just give the new response: 
    I've been learning gardening, it's been so fun!. 
    

    Another example:
    If the query is: "Hey Jane, what are you up to?"
    and the responses previously generated were:
    ["Hi Gary, I've been dancing recently.", "Hey Gary, I've been hiking recently!", "Hey Gary, I've been learning gardening, how about you?"]
    and the scores are [0, 1, 0.5] respectively,
    then, the good response is: "Hey Gary, I've been hiking recently!"?
    and the bad response is "Hi Gary, I've been dancing recently."

    The generated response should not be about dancing and should be about hiking (using the good response as a guide to infer the topic).
    Do not not repeat any previous responses like "Hey Gary, I've been hiking recently!"  
    Do not explain reasoning and just give the new response: : 
    "I've been hiking recently and its my new hobby".
    """

    # Learning instructions
    instruction = {
        "role": "system",
        "content": meta_content,
    }

    # Initialize messages
    messages = []

    # Add learn instruction to message array
    messages.append(instruction)

    user_message = {
            "role": "user",
            "content": query
    }

    messages.append(user_message)

    raw_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages = messages,
    )
    newResponse = raw_response.choices[0].message.content

    return(newResponse)

#--------------------------------------------- Storage ---------------------------------------------

# Add conversation into respective person's json
def store_conversation(filename, mute, normal, query, response):
    try:
        # Load existing data from the JSON file
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
        else:
            data = {}

        # Determine the next response number
        next_response_number = len(data) + 1
        response_key = f"Response {next_response_number}"

        # Append new response
        data[response_key] = {
            normal: query,
            mute: response
        }

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        # Vector store adding
        add_to_vector_store(filename, mute, normal, query, response, get_stored_topic(), response_key)

        return {"message": "Response stored successfully"}

    except Exception as e:
       print("Error is:", e)
       return

# Adds the response and vectorizes
def add_to_vector_store(filename, mute, normal, query, response, topic, response_key):
    vectorized_response = {
        f"{normal}": query,
        f"{mute}": response,
    }

    vectorized_response_str = json.dumps(vectorized_response)
    vector_id = uuid4()

    doc_metadata = {"label": response_key, "source": filename,  'file_name': filename, 'topic': topic, 'id': vector_id}
    print(doc_metadata)

    try:
        response_document = Document(page_content=vectorized_response_str, metadata=doc_metadata)
    except Exception as e:
        print(e)
        return

    documents = [response_document]
    ids=[vector_id]

    loaded_faiss_vs_hf_v3.add_documents(documents=documents, ids=ids)
    # "C:\\Roydon\\Github\\FYP_Application\\MuteCompanion\\backend\\vector_store\\vectorstores\\hugging_face\\faiss_vs_hf_v3_new"
    # C:\\Roydon\\Github\\FYP_Application\\MuteCompanion\\MuteApp\\assets\\mockdata\\Jane\\faiss_vectorstore_Jane_V2
    
    loaded_faiss_vs_hf_v3.save_local("C:\\Roydon\\Github\\FYP_V2\\muteApp\\assets\\mockdata\\Jane\\faiss_vectorstore_Jane_V2") # Remember to save else when reinitialize, variables gone
    print("Vector Added successfully")

    # Add to documents list
    store_documents(json_file_path= json_file_path, page_content=vectorized_response, meta_data=doc_metadata)

    # Reinitialize variables for reuse
    initialize_variables()

def delete_from_vector_store(source):
    # Search vector store to delete
    results = loaded_faiss_vs_hf_v3.similarity_search(
        "",
        k=1,
        filter={"source": source},
    )

    result_id = results[0].metadata['id']

    # Delete from vector store
    loaded_faiss_vs_hf_v3.delete(ids=[result_id])
    loaded_faiss_vs_hf_v3.save_local("C:\\Roydon\\Github\\FYP_V2\\muteApp\\assets\\mockdata\\Jane\\faiss_vectorstore_Jane_V2") # Remember to save else when reinitialize, variables gone
    print("Deleted successfully")

    # Reinitialize variables for reuse
    initialize_variables()






    








