import {
  Text,
  View,
  StyleSheet,
  FlatList,
  Image,
  TouchableOpacity,
} from "react-native";
import SearchBar from "../components/UI/SearchBar";

// Data for the chat items
import garyData from "../assets/mockdata/Jane/Gary.json";
import jacksonData from "../assets/mockdata/Jane/Jackson.json";
import maryData from "../assets/mockdata/Jane/Mary.json";
import mattData from "../assets/mockdata/Jane/Matt.json";
import nattyData from "../assets/mockdata/Jane/Natty.json";
import xavierData from "../assets/mockdata/Jane/Xavier.json";

// Display the last message snippet
function getLastMessageSnippet(data) {

  const responseKeys = Object.keys(data);
  const lastResponseKey = responseKeys[responseKeys.length - 1]; // Get the latest response
  const lastMessage = data[lastResponseKey]["Jane"]; // Get the message from the mute user
  return lastMessage.length > 13 ? `${lastMessage.substring(0, 15)}...` : lastMessage; // Return the first 13 characters plus ... if longer
}


const chatData = [
  {
    id: "1",
    name: "Gary Lim",
    message: getLastMessageSnippet(garyData),
    allMessages: garyData,
    chatType: "historical",
    time: "9:00 pm",
    imageUrl: require("C:\\Roydon\\Github\\FYP_V2\\muteApp\\assets\\man1.jpg"),
  },
  {
    id: "2",
    name: "Jackson Tan",
    message: getLastMessageSnippet(jacksonData),
    allMessages: jacksonData,
    chatType: "historical",
    time: "9:00 pm",
    imageUrl: require("C:\\Roydon\\Github\\FYP_V2\\muteApp\\assets\\man2.jpg"),
  },
  {
    id: "3",
    name: "Mary Tan",
    message: getLastMessageSnippet(maryData),
    allMessages: maryData,
    chatType: "historical",
    time: "9:00 pm",
    imageUrl: require("C:\\Roydon\\Github\\FYP_V2\\muteApp\\assets\\woman1.jpg"),
  },
  {
    id: "4",
    name: "Matt Boey",
    message: getLastMessageSnippet(mattData),
    allMessages: mattData,
    chatType: "historical",
    time: "9:00 pm",
    imageUrl: require("C:\\Roydon\\Github\\FYP_V2\\muteApp\\assets\\man3.jpg"),
  },
  {
    id: "5",
    name: "Natty Toh",
    message: getLastMessageSnippet(nattyData),
    allMessages: nattyData,
    chatType: "historical",
    time: "9:00 pm",
    imageUrl: require("C:\\Roydon\\Github\\FYP_V2\\muteApp\\assets\\woman2.jpg"),
  },
  {
    id: "6",
    name: "Xavier Oh",
    message: getLastMessageSnippet(xavierData),
    allMessages: xavierData,
    chatType: "historical",
    time: "9:00 pm",
    imageUrl: require("C:\\Roydon\\Github\\FYP_V2\\muteApp\\assets\\man4.jpg"),
  },
];

function AllChat({ navigation }) {
  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.chatItem}
      onPress={() =>
        navigation.navigate("Chat", {
          chatId: item.id,
          chatName: item.name,
          allMessages: item.allMessages,
          chatType: item.chatType,
        })
      }
    >
      <Image source={item.imageUrl} style={styles.profilePic} />
      <View style={styles.chatInfo}>
        <Text style={styles.chatName}>{item.name}</Text>
        <Text style={styles.chatSnippet}>{item.message}</Text>
      </View>
      <Text style={styles.chatTime}>{item.time}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <SearchBar />
      <FlatList
        data={chatData}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
      />
      {/* <View style = {styles.textContainer}>
        <Text style={styles.text}>Testing All Chat</Text>
      </View> */}
    </View>
  );
}

export default AllChat;

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  chatItem: {
    flexDirection: "row",
    padding: 15,
    alignItems: "center",
    borderBottomWidth: 2,
    borderBottomColor: "#ccc",
  },
  profilePic: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginRight: 10,
  },
  chatInfo: {
    flex: 1,
    justifyContent: "center",
  },
  chatName: {
    fontSize: 16,
    fontWeight: "bold",
  },
  chatSnippet: {
    fontSize: 14,
    color: "grey",
  },
  chatTime: {
    fontSize: 12,
    color: "grey",
  },
  // textContainer: {
  //   flex: 1, // Takes the remaining space after the SearchBar
  //   justifyContent: 'center',
  //   alignItems: 'center',
  // },

  // text: {
  //   fontSize: 16, // You can adjust the font size as needed
  //   textAlign: "center", // Ensures the text is centered if it wraps to a new line
  // },
});
