import { getDatabase } from "firebase/database"
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";


const firebaseConfig = {
  apiKey: "AIzaSyBIeoOfmmLeUhhm9AY33izdevcU-ABxjhY",
  authDomain: "predictchain-1e4f4.firebaseapp.com",
  databaseURL: "https://predictchain-1e4f4-default-rtdb.firebaseio.com",
  projectId: "predictchain-1e4f4",
  storageBucket: "predictchain-1e4f4.appspot.com",
  messagingSenderId: "998058245249",
  appId: "1:998058245249:web:ea8b9eeb08e7279f75e180",
  measurementId: "G-7GTBG52EBJ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
export const database = getDatabase(app);