import { View, TextInput, StyleSheet } from "react-native";
import { GlobalStyles } from "../../constants/styles";

function SearchBar() {
  return (
    <View style={styles.container}>
      <TextInput placeholder="Search for chat..." style={styles.input} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    paddingHorizontal: 10,
    paddingVertical: 10,
    backgroundColor: GlobalStyles.colors.primary100,
    borderTopWidth: 0,
    borderBottomWidth: 0
  },
  input: {
    borderWidth: 1,
    borderColor: 'grey',
    padding: 10,
    borderRadius: 5,
    backgroundColor: 'white',
  }
});

export default SearchBar;