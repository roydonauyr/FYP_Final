import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View, TouchableOpacity } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { GlobalStyles } from "./constants/styles";
import { useEffect } from "react";

// Navigation
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";

// Screens
import AllChat from "./screens/AllChat";
import UpcomingEvents from "./screens/UpcomingEvents";
import Profile from "./screens/Profile";
import Chat from "./screens/Chat";

//Create Navigation items
const Stack = createNativeStackNavigator();
const BottomTabs = createBottomTabNavigator();

// Other components
import IconButton from "./components/UI/IconButton";
import EntypoButton from "./components/UI/EntypoButton";
import SearchBar from "./components/UI/SearchBar";
import ChatContextProvider from "./components/Chats/chat-context";

import { Audio } from "expo-av";

async function getMicrophonePermissions() {
  const { status } = await Audio.requestPermissionsAsync();
  if (status === "granted") {
    console.log("Microphone permissions granted.");
    // You can now proceed to record audio
  } else {
    console.log("Microphone permissions denied.");
    // Handle the denied case appropriately
  }
}

function MainOverview() {
  return (
    <BottomTabs.Navigator
      screenOptions={({ navigation }) => ({
        headerStyle: {
          backgroundColor: GlobalStyles.colors.primary100,
          shadowOpacity: 0, // remove shadow on iOS
          elevation: 0, // remove shadow on Android
        },
        headerTintColor: "white",
        tabBarStyle: { backgroundColor: GlobalStyles.colors.primary100 },
        tabBarActiveTintColor: GlobalStyles.colors.accent500,
        headerRight: ({ tintColor }) => (
          <EntypoButton
            icon="new-message"
            size={24}
            color={tintColor}
            onPress={() => {
              navigation.navigate("Chat");
            }}
          />
        ),
      })}
    >
      <BottomTabs.Screen
        name="AllChat"
        component={AllChat}
        options={{
          title: "All Chat",
          tabBarLabel: "All Chat",
          tabBarIcon: ({ color, size }) => (
            <EntypoButton icon="chat" size={size} color={color} />
          ),
        }}
      />
      <BottomTabs.Screen
        name="Upcoming Events"
        component={UpcomingEvents}
        options={{
          title: "Upcoming Events",
          tabBarLabel: "Upcoming Events",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="calendar" size={size} color={color} />
          ),
        }}
      />
      <BottomTabs.Screen
        name="Profile"
        component={Profile}
        options={{
          title: "Profile",
          tabBarLabel: "Profile",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="settings" size={size} color={color} />
          ),
        }}
      />
    </BottomTabs.Navigator>
  );
}

export default function App() {
  useEffect(() => {
    getMicrophonePermissions();
  }, []);

  return (
    <>
      <StatusBar style="light" />
      <ChatContextProvider>
        <NavigationContainer>
          <Stack.Navigator
            screenOptions={{
              headerStyle: { backgroundColor: GlobalStyles.colors.primary100 },
              headerTintColor: "white",
            }}
          >
            <Stack.Screen
              name="MainOverview"
              component={MainOverview}
              options={{ headerShown: false }}
            />
            <Stack.Screen
              name="Chat"
              component={Chat}
              options={({ route, navigation }) => ({
                title: route.params?.chatName || "New Chat",
                headerLeft: () => (
                  <TouchableOpacity
                    onPress={() => navigation.goBack()}
                    style={{ marginLeft: 10 }}
                  >
                    <Ionicons name="arrow-back" size={24} color="white" />
                  </TouchableOpacity>
                ),
              })}
            />
          </Stack.Navigator>
        </NavigationContainer>
      </ChatContextProvider>
    </>
  );
}
