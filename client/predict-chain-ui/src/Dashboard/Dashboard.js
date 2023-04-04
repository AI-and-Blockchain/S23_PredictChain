import React, { useEffect, useState } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";
import { auth, db, logout } from "../firebase";
import { query, collection, getDocs, where } from "firebase/firestore";
import axios from "axios";

function Dashboard() {
  const [user, loading, error] = useAuthState(auth);
  const [name, setName] = useState("");
  const [pk, setPK] = useState("");
  const [addr, setAddr] = useState("");
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);

  const handleUpdateState = () => {
    axios.get('http://localhost:8031/update_state')
      .then(response => {setTransactions(response.data.transactions); console.log(response);})
      .catch(error => console.error(error));
  }


  const fetchUserName = async () => {
      const q = query(collection(db, "users"), where("uid", "==", user?.uid));
      const doc = await getDocs(q);
      const data = doc.docs[0].data();
      setName(data.name);
      setPK(data.privateKey);
      setAddr(data.address);
  };

  useEffect(() => {
    if (loading) return;
    if (!user) return navigate("/");

    fetchUserName();
  }, [user, loading]);

  return (
    <div>
      <div className="fixed-header">
        <nav>
          <a href="/" style={{fontSize: 'xx-large', fontWeight: '900', color: '#ffffff', marginRight: '80px', marginLeft: '100px'}}>PredictChain</a>
          <a href="/faq"style={{marginLeft: '500px'}}>FAQ</a>
          <a href="/mtt" style={{marginLeft: '300px'}}>Meet The Team</a>
          <a href="https://github.com/AI-and-Blockchain/S23_PredictChain" style={{marginLeft: '300px'}}>Docs</a>
        </nav>       
      </div>
      <div className="dashboard">
        <div className="dashboard__container">
          <h1 style={{textAlign: "left", marginLeft: "50px"}}>Welcome {name}!</h1>
          Logged in as
          <div>{name}</div>
          <div>{user?.email}</div>
          <div><h2>Private Key:</h2> {pk}</div>
          <div><h2>Address:</h2> {addr}</div>
          <button className="dashboard__btn" onClick={logout}>
            Logout
          </button>
        </div>
      </div>
      <div>
        <button onClick={handleUpdateState}>Update State</button>
        <ul>
          {transactions.map((txn, index) => (
            <li key={index}>{txn}</li>
          ))}
        </ul>
      </div>
      <div className="fixed-footer">
          <nav>
            <a href="/" style={{fontSize: 'xx-large', fontWeight: '900', color: '#ffffff', marginRight: '80px', marginLeft: '100px'}}>PredictChain</a>
            <a href="/faq"style={{marginLeft: '400px'}}>FAQ</a>
            <a href="/mtt" style={{marginLeft: '200px'}}>Meet The Team</a>
            <a href="https://github.com/AI-and-Blockchain/S23_PredictChain" style={{marginLeft: '200px'}}>Docs</a>
            <a href="#" style={{marginLeft: '200px'}}>Back to top</a>
          </nav>       
        </div>
    </div>
  );
}

export default Dashboard;