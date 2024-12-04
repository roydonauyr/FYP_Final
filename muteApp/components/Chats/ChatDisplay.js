import { useContext, useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, TextInput } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { GlobalStyles } from "../../constants/styles";

//Context
import { ChatContext } from "./chat-context";

function ChatDisplay({
  messageId,
  responses,
  rank_and_regenerate,
  onChooseReply,
  onRegenerateResponses,
}) {
  const chatCtx = useContext(ChatContext);

  // Find the selected response for the current message
  const selectedResponse = chatCtx.replyChosen.find(
    (reply) => reply.id === messageId
  )?.reply;

  // Regeneration Of Single Response Through Ranking
  const [scores, setScores] = useState(new Array(responses.length).fill(0.5));

  // Editing Of Response
  const [editIndex, setEditIndex] = useState(-1);
  const [editText, setEditText] = useState("");

  //----------------------------------FUNCTIONS----------------------------------------------

  // Choosing of replies
  function handleResponseSelection(response) {
    if (editIndex == -1) {
      onChooseReply(messageId, response); // Only can choose a reply if not editing
    }
  }

  // Updating regeneration of responses
  const handleRegenerateResponses = () => {
    onRegenerateResponses(messageId);
  };

  // Ranking and regenerating bad responses
  const rank_and_store = async (index, score) => {
    const newScores = [...scores];
    newScores[index] = score;
    setScores(newScores);

    // Only for thumbs down
    if (score === 0) {
      const currentResponses = [...responses];
      const replacedResponse = currentResponses[index];
      console.log("Current Bad Response: ", replacedResponse);

      const newResponse = await rank_and_regenerate(
        newScores,
        currentResponses,
        replacedResponse
      );
      currentResponses[index] = newResponse;
      newScores[index] = 0.5;

      // Update the response in the context
      chatCtx.updateResponses(messageId, currentResponses);
      setScores(newScores); // Update the new option to be a neutral score
    }
  };

  // Editing Of Response
  function handleEditResponse(response, idx) {
    setEditIndex(idx);
    setEditText(response);
  }

  // Function to cancel editing
  function handleCancelEdit() {
    setEditIndex(-1);
    setEditText("");
  }

  // Function to save the edited response
  function handleSaveEdit() {
    const updatedResponses = [...responses];
    updatedResponses[editIndex] = editText;
    chatCtx.updateResponses(messageId, updatedResponses);
    setEditIndex(-1);
    setEditText("");
  }

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.refreshButton}
        onPress={handleRegenerateResponses}
      >
        <Ionicons
          name="refresh"
          size={24}
          color={GlobalStyles.colors.primary200}
        />
      </TouchableOpacity>
      {responses.map((response, idx) => (
        <View key={idx} style={styles.responseContainer}>
          {editIndex === idx ? (
            <>
              <TextInput
                style={styles.input}
                value={editText}
                onChangeText={setEditText}
              />
              <TouchableOpacity onPress={handleSaveEdit} style={styles.icon}>
                <Ionicons name="checkmark" size={24} color="green" />
              </TouchableOpacity>
              <TouchableOpacity onPress={handleCancelEdit} style={styles.icon}>
                <Ionicons name="close" size={24} color="red" />
              </TouchableOpacity>
            </>
          ) : (
            <>
              <TouchableOpacity
                style={styles.editButton}
                onPress={() => handleEditResponse(response, idx)}
              >
                <Ionicons name="create-outline" size={24} color="blue" />
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.responseButton}
                onPress={() => handleResponseSelection(response)}
              >
                <Text style={styles.responseText}>{response}</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => rank_and_store(idx, 1)} style={styles.icon}>
                <Ionicons name="thumbs-up" size={24} color="green" />
              </TouchableOpacity>
              <TouchableOpacity onPress={() => rank_and_store(idx, 0)} style={styles.icon}>
                <Ionicons name="thumbs-down" size={24} color="red" />
              </TouchableOpacity>
            </>
          )}
        </View>
      ))}
      {selectedResponse && (
        <Text style={styles.selectedResponseText}>{selectedResponse}</Text>
      )}
    </View>
  );
}

export default ChatDisplay;

const styles = StyleSheet.create({
  container: {
    marginHorizontal: 10,
    backgroundColor: "#fff", // Optional: changes background of the response area
    paddingTop: 45,
    paddingBottom: 10,
    paddingLeft: 10,
    paddingRight: 10,
    borderRadius: 10, // Rounded corners for the container
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  responseContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 10,
  },
  refreshButton: {
    position: "absolute",
    top: 10,
    left: 10,
    padding: 5,
    zIndex: 10, // Make sure it is above other elements
  },
  responseButton: {
    backgroundColor: GlobalStyles.colors.primary100,
    padding: 10,
    marginTop: 5,
    borderRadius: 5,
    width: "65%", // Makes buttons occupy only 80% of the width
    alignSelf: "center", // Centers button in the container
  },
  icon: {
    padding: 5,
  },
  responseText: {
    color: "white",
    backgroundColor: GlobalStyles.colors.primary100,
    padding: 10,
    borderRadius: 5,
    flex: 1,
    marginHorizontal: 10,
    textAlign: "center", // Center align text within the button
  },
  selectedResponseText: {
    marginTop: 10,
    fontSize: 16,
    color: GlobalStyles.colors.primary100,
    textAlign: "center", // Center align the selected response text
    paddingTop: 5,
    borderTopWidth: 1, // Adds a line above the selected response
    borderTopColor: GlobalStyles.colors.primary100,
  },
  input: {
    flex: 1,
    borderColor: 'gray',
    borderWidth: 1,
    padding: 10,
    borderRadius: 5,
    color: 'black',
    backgroundColor: 'white',
  },
});
