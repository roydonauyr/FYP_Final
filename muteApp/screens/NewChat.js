import React, { useState } from "react";
import { Modal, View, TextInput, Button, StyleSheet } from "react-native";

// Declare ip
import { config } from "../components/Config/config";

function NewChat({ isVisible, onClose, onSave }) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");

  const handleSave = async () => {
    const result = await createNewChat(firstName, lastName);
    onSave({ firstName, lastName }); // Pass the new chat details back up
    onClose(); // Close the modal
  };

  return (
    <Modal visible={isVisible} animationType="slide" transparent={true}>
      <View style={styles.modalBackground}>
        <View style={styles.modalContainer}>
          <TextInput
            placeholderTextColor={"#ccc"}
            style={styles.input}
            placeholder="First Name"
            value={firstName}
            onChangeText={setFirstName}
          />
          <TextInput
            placeholderTextColor={"#ccc"}
            style={styles.input}
            placeholder="Last Name"
            value={lastName}
            onChangeText={setLastName}
          />
          <Button title="Save" onPress={handleSave} color="#5cb85c" />
          <Button title="Cancel" onPress={onClose} color="#d9534f" />
        </View>
      </View>
    </Modal>
  );
}

async function createNewChat(firstName, lastName) {
  const formData = new FormData();

  // Add selected response if not null
  formData.append("first_name", firstName);
  formData.append("last_name", lastName);

  try {
    const response = await fetch(
      `http://${config.apiBaseUrl}:8000/create-chat/`,
      {
        method: "POST",
        body: formData,
      }
    );
  } catch (error) {
    console.error("Failed to create new person:", error);
  }
}

const styles = StyleSheet.create({
  modalBackground: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(0,0,0,0.5)",
  },
  modalContainer: {
    width: "80%",
    backgroundColor: "white",
    paddingHorizontal: 20,
    paddingVertical: 30,
    borderRadius: 10,
    elevation: 20,
  },
  input: {
    backgroundColor: "white", // Ensuring background is white
    height: 40,
    marginVertical: 12,
    borderWidth: 1,
    padding: 10,
    borderRadius: 5,
    borderColor: "#ccc",
    color: "black",
  },
});

export default NewChat;
