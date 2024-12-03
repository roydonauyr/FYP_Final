import json
import os
from nltk.tokenize.punkt import PunktSentenceTokenizer
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# Get topic from the conversation
# Initiate meta content
meta_content = """
You would be assisting in identifying topics from a snippet of conversation. I would supply the conversation directly. 
Interpret the main topic of the conversation and return the main topic.

Do not give multiple topics such as football/soccer. Only give one main topic.

For example if the conversation is: 
            {"Roydon": "Can't wait for the new football season to start, hoping for a great one for Arsenal!", "John": "Hey Roydon! Yeah, it's 
            always exciting to see how your team will perform."}

            football

            Example 2:
            {"Roydon": "I'm planning to go on a trip to Japan next year", "John": "That's awesome! Japan is such a beautiful country."}

            travel

            Example 3: If no main topic can be determined such as a greeting
            {"Roydon": "Hey there! How are you doing?", "John": "Hey Roydon! I'm doing great, how about you?"}

            general 
"""

global final_topic

def is_valid_word(word):
    """Check if a word is valid by looking it up in WordNet."""
    return bool(wordnet.synsets(word))

def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts."""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)

def remove_ing(topic):
    if topic.endswith('ing'):
        return topic[:-3]
    return topic

# Filtering functions
def singularize_and_lower(topic):
    # Initialize the WordNet Lemmatizer
    lemmatizer = WordNetLemmatizer()
    
    # Lowercase the topic
    topic = topic.lower()

    # Lemmatize the word with correct POS tag
    pos = get_wordnet_pos(topic)
    topic_lemmataized = lemmatizer.lemmatize(topic, pos)

    # Extra check for words like crotcheting
    topic = remove_ing(topic_lemmataized)
    processed_words = [is_valid_word(word) for word in topic.split()]
    if not all(processed_words):
        return topic_lemmataized
        
    return topic

def filter_list(docs_rel, topic):
    # Filter according to the topic
    filtered_docs = []
    final_docs = []
    general_topic = {}

    if singularize_and_lower(topic) == "general":
        for doc in docs_rel:
            if singularize_and_lower(doc.metadata['topic']) not in general_topic:
                general_topic[singularize_and_lower(doc.metadata['topic'])] = 1
                filtered_docs.append(doc)
            else:
                continue
    else:
        for doc in docs_rel:
            if(singularize_and_lower(doc.metadata['topic']) == singularize_and_lower(topic)):
                filtered_docs.append(doc)
       
    if len(filtered_docs) > 2:
        final_docs = filtered_docs[:3]
        return final_docs
    else:
        count = 3 - len(filtered_docs)
        final_docs = filtered_docs
        position = 0
        for i in range(count):
            if(position == len(docs_rel)):
                break
            if(docs_rel[position] in filtered_docs):
                i = i-1
                position += 1
                continue
            else:
                final_docs.append(docs_rel[position])# need to change so that it wont be same obtained
                position+=1 
        
        return final_docs
    
# Process query
def process_query(query):
    # Initialize the Punkt tokenizer
    tokenizer = PunktSentenceTokenizer()
    
    # Tokenize the text into sentences
    sentences = tokenizer.tokenize(query)

    # Check if the query is a simple one (contains only one sentence)
    if len(sentences) == 1:
        return sentences  # Return the single sentence wrapped in a list

    # Combine into segments
    combined = ''
    segments = []

    # Flag to check if last sentence was a question
    last_was_question = False

    # Loop through each sentence and decide whether to start a new segment
    for sentence in sentences:
        # If last sentence was a question and current isn't directly a question,
        # start a new segment
        if last_was_question and sentence.strip().endswith('?'):
            segments.append(combined.strip())
            combined = sentence + ' '
            last_was_question = False
        else:
            combined += sentence + ' '

        # Check if current sentence ends with a question mark
        if sentence.strip().endswith('?'):
            last_was_question = True

    # Append the last segment if there's any remaining text
    if combined:
        segments.append(combined.strip())

    return segments

#The 3 responses must be seperated by an @, for example: "Response 1 generated@Response 2generated@Response 3 generated" all in one line and 
# Start by generating 3 responses to what the other person says.
        # After generating the 3 responses, you will then receive the following for all subsequent conversations
        # Roydon says: ... Other person says ... After which generate the 3 responses.
# Get recent messages
def get_previous_responses(getTopic, ensemble_retriever, query, search, fail_safe_retriever, mute, normal, meta_content = meta_content):

    json_file = "data.json"
    
    # Initialize messages
    messages = []

    if(search):
        
        #context = loaded_faiss_vs.similarity_search(query, k=3)
        # contexts = ""

        # for con in context:
        #     contexts += con.page_content

        print(f"Normal person says: {query}\n")

        contexts = ""
        query_split = process_query(query)
        for i in query_split:
            # Obtain top 3 filtered docs
            try:
                docs_rel=ensemble_retriever.invoke(i)
                topic_interpreted = getTopic(meta_content, i)
                final_docs = filter_list(docs_rel, topic_interpreted) # Still top 3
                global final_topic
                final_topic = topic_interpreted
                for context in final_docs:
                    contexts += context.page_content
            except Exception as e:
                print("Entered fail safe")
                context = fail_safe_retriever.similarity_search(query, k=3)
                for con in context:
                    contexts += con.page_content
            


        content = f"""You are an assistant whom will faciliate the conversation between a mute and a normal person. The mute persons name is {mute} and the normal person is indicated as {normal}.
                        You should be generating 3 responses which the mute person could choose from and the responses generated should follow the context of the conversation. 
                        The responses should be what a person would say and should not include actions in a third person view. Your persona would be from the perspective of the mute person.

                        Snippets of conversation would be given below in the section of Context. Use the conversations to assist in the generation the 3 responses. Primarily the topic should be inferred from the question asked but if no topic can be inferred, infer the topics from the conversations given in the context. The conversations are seperated by "{{" and "}}":\n
                        Context: {contexts}

                        For example, if the context above contains "{{"Roydon": "Recently my new pet dog has been so fun!", "Jacob": "That\'s awesome! What breed is it?"}}"

                        If the user asks "What have you been up to?"

                        An example of the 3 generated response would be in the format of 1 single string "Response 1: I have been playing with my new pet dog. Response 2: Nothing much, I recently brought my new pet dog to a park. Response 3: Its been tiring lately after getting a new pet dog.
                                """
                            
        print("This is the context: " + contexts)

        # Learning instructions
        instruction = {
            "role": "system",
            "content": content,
        }


        # # Add personality to the chatbot
        # rand_num = random.uniform(0,1)

        # if (rand_num < 0.3):
        #     instruction["content"] = instruction["content"] + "Out of the 3 responses, include some dry humour in at least 1."

        # Add learn instruction to message array
        messages.append(instruction)

    #Get last 5 messages
    try:
        with open(json_file) as user_messages:
            data = json.load(user_messages)
            
            if data:
                if len(data) < 5:
                    for message in data:
                        messages.append(message)
                else:
                    for message in data[-5:]:
                        messages.append(message)
    except Exception as e:
        print(e)
        pass

    # Return
    return messages


# Store messages into json file:
def store_messages(user_message, gpt_response):

    json_file = "data.json"
    embeddings = ''
    getTopic = ()

    # Get recent messages and exclude first response:
    messages = get_previous_responses(getTopic, embeddings, query = user_message, search=False, fail_safe_retriever='', mute = '', normal = '')

    # Store user response:
    user_response = {
        "role": "user", 
        "content": user_message
    }

    # Store chatgpt generated response
    chat_gpt_response = {
        "role": "assistant", 
        "content": gpt_response
    }

    messages.append(user_response)
    messages.append(chat_gpt_response)

    # Save and overwrite json file
    with open(json_file, "w") as f:
        json.dump(messages,f)

# Store all documents into json file:
def store_documents(json_file_path, page_content, meta_data): 
    try:
        # Load existing data from the JSON file
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as file:
                data = json.load(file)
        else:
            print("Unable to store into documents file, does not exist")
            return

        meta_data["id"] = f"{meta_data['id']}"

        # save the new response
        new_response = {
            "metadata": meta_data,
            "page_content": f"{page_content}"
        }

        # Append new response
        data.append(new_response)

        with open(json_file_path, "w") as file:
            json.dump(data, file, indent=4)
        
        print("Documents added to all documents file")
    except Exception as e:
       print("Error is:", e)
       return


# Get Topic Stored (Minimise reruns)
def get_stored_topic():
    return final_topic


# Reset messages stored in json file
def reset_messages():
    # Overwrite current json file with nothing
    open("data.json", "w")