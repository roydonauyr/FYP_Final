import { createContext, useReducer } from "react";

// Defining the chat structure
const initialState = {
  messages: [], // Dictionary containing text and choices
  replyChosen: [],
};

export const ChatContext = createContext({
  ...initialState,
  addMessage: (message) => {},
  chooseReply: (messageId, reply) => {},
  clearMessages: () => {},
  updateResponses: (messageId, newResponses) => {},
});

function chatReducer(state, action) {
  switch (action.type) {
    case "ADD_MESSAGE":
      return {
        ...state,
        messages: [...state.messages, {...action.payload, replyIndex: state.messages.length}],
      };
    case "CHOOSE_REPLY":
      return {
        ...state,
        replyChosen: [...state.replyChosen, {reply: action.payload, id: action.messageId}],
      };
    case "CLEAR_MESSAGES":
      return initialState;
    case "UPDATE_RESPONSES":
      const updatedMessages = state.messages.map(message =>
        message.id === action.messageId ? { ...message, responses: action.payload } : message
      );
      return {
        ...state,
        messages: updatedMessages
      };
    default:
      return state;
  }
}

function ChatContextProvider({ children }){
    const [chatState, dispatch] = useReducer(chatReducer, initialState);
    
    // message would be the dictionary containing text and choices
    function addMessage(message){
      dispatch({ type: "ADD_MESSAGE", payload: message });
    }
    
    // reply would be the choice made by the user
    function chooseReply(messageId, reply){
      dispatch({ type: "CHOOSE_REPLY", payload: reply, messageId: messageId});
    }

    //Clear messages and return to intial state
    function clearMessages(){
      dispatch({ type: "CLEAR_MESSAGES"});
    }

    // Update responses when regenerating responses
    function updateResponses(messageId, newResponses){
      dispatch({ type: "UPDATE_RESPONSES", messageId, payload: newResponses});
    }

    const value = {
        ...chatState,
        addMessage: addMessage,
        chooseReply: chooseReply,
        clearMessages: clearMessages,
        updateResponses: updateResponses,
    };
    
    return (
        <ChatContext.Provider value={value}>
        {children}
        </ChatContext.Provider>
    );
}

export default ChatContextProvider;
