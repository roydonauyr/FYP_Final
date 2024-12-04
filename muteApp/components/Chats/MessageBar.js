import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Animated,
  KeyboardAvoidingView, 
  Platform
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { GlobalStyles } from "../../constants/styles";
import { useState, useEffect } from "react";

function MessageBar({
  activeId,
  onSendMessage,
  onSendVoiceMessage,
  currentMessage,
  onChangeMessage,
  style,
}) {
  const [isRecording, setIsRecording] = useState(false);
  const [iconOpacity] = useState(new Animated.Value(1));

  function handleRecording() {
    if (isRecording) {
      onSendVoiceMessage.stop();
      setIsRecording(false);
    } else {
      onSendVoiceMessage.start();
      setIsRecording(true);
    }
  }

  useEffect(() => {
    let animation;
    if (isRecording) {
      animation = Animated.loop(
        Animated.sequence([
          Animated.timing(iconOpacity, {
            toValue: 0.2,
            duration: 500, // fade out for 500ms
            useNativeDriver: true,
          }),
          Animated.timing(iconOpacity, {
            toValue: 1,
            duration: 500, // fade in for 500ms
            useNativeDriver: true,
          }),
        ])
      );
      animation.start();
    } else {
      iconOpacity.setValue(1); // Reset opacity if not recording
      animation && animation.stop();
    }
    return () => {
      animation && animation.stop();
    };
  }, [isRecording, iconOpacity]);

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={Platform.OS === "ios" ?  95: 0}
    >
      <View style={styles.container}>
        <TextInput
          style={styles.input}
          placeholder="Send a message"
          value={currentMessage}
          onChangeText={onChangeMessage}
        />
        <TouchableOpacity
          onPress={() => onSendMessage(currentMessage, activeId)}
        >
          <Ionicons
            name="send"
            size={24}
            color={GlobalStyles.colors.primary100}
            style={styles.iconButton}
          />
        </TouchableOpacity>
        <TouchableOpacity onPress={() => handleRecording()}>
          <Ionicons
            name={isRecording ? "stop-circle" : "mic"}
            size={24}
            color={isRecording ? "red" : GlobalStyles.colors.primary100}
            style={[styles.iconButton, isRecording && styles.blinking]}
          />
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

export default MessageBar;

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    padding: 15,
    backgroundColor: "white",
    borderTopWidth: 1,
    borderColor: "lightgrey",
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: "grey",
    padding: 10,
    marginRight: 10,
    borderRadius: 10,
  },
  iconButton: {
    padding: 10,
  },
  blinking: {
    opacity: 0.5,
  },
});
