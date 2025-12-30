import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './screens/HomeScreen';
import IncidentReportScreen from './screens/IncidentReportScreen';
import EmergencyContactsScreen from './screens/EmergencyContactsScreen';

const Stack = createStackNavigator();

const App = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Report Incident" component={IncidentReportScreen} />
        <Stack.Screen name="Emergency Contacts" component={EmergencyContactsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;