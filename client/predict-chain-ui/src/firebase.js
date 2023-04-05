import { initializeApp } from "firebase/app";
import {
  GoogleAuthProvider,
  getAuth,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  signOut,
} from "firebase/auth";
import {
  getFirestore,
  query,
  getDocs,
  collection,
  where,
  addDoc,
} from "firebase/firestore";
import axios from 'axios';


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

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

const googleProvider = new GoogleAuthProvider();

const signInWithGoogle = async () => {
  try {
    const res = await signInWithPopup(auth, googleProvider);
    const user = res.user;
    axios.post('http://localhost:8031/new_account')
      .then(response => {
        const address = response.data.address; 
        const privateKey = response.data.private_key;
        addDoc(collection(db, "users"), {
          uid: user.uid,
          name: user.displayName,
          authProvider: "google",
          email: user.email,
          privateKey: privateKey,
          address: address
        });
    });
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
};

const logInWithEmailAndPassword = async (email, password) => {
  try {
    await signInWithEmailAndPassword(auth, email, password);
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
};

const registerWithEmailAndPassword = async (name, email, password) => {
  let address, privateKey; // Declare the variables outside of the callback function
  try {
    axios.post('http://localhost:8031/new_account')
      .then(response => {
        address = response.data.address; // Assign the values inside the function
        privateKey = response.data.private_key;
    });
    const res = await createUserWithEmailAndPassword(auth, email, password);
    const user = res.user;
    await addDoc(collection(db, "users"), {
      uid: user.uid,
      name,
      authProvider: "local",
      email,
      privateKey: privateKey,
      address: address,
    });
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
};


const sendPasswordReset = async (email) => {
  try {
    await sendPasswordResetEmail(auth, email);
    alert("Password reset link sent!");
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
};

const logout = () => {
  signOut(auth);
};

export {
  auth,
  db,
  signInWithGoogle,
  logInWithEmailAndPassword,
  registerWithEmailAndPassword,
  sendPasswordReset,
  logout,
};