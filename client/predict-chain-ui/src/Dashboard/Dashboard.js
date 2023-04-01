import React, { useEffect, useState } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";
import { auth, db, logout } from "../firebase";
import { query, collection, getDocs, where } from "firebase/firestore";

function Dashboard() {
  const [user, loading, error] = useAuthState(auth);
  const [name, setName] = useState("");
  const navigate = useNavigate();

  const fetchUserName = async () => {
      const q = query(collection(db, "users"), where("uid", "==", user?.uid));
      const doc = await getDocs(q);
      const data = doc.docs[0].data();

      setName(data.name);
  };

  useEffect(() => {
    if (loading) return;
    if (!user) return navigate("/");

    fetchUserName();
  }, [user, loading]);

  return (
    <div>
      <div className="fixed-footer">
        <nav>
          <a href="javascript:void(0)" style={{fontSize: 'xx-large', fontWeight: '900', color: '#ffffff', marginRight: '80px', marginLeft: '100px'}}>PredictChain</a>
          <a href="javascript:void(0)"style={{marginLeft: '100px'}}>FAQ</a>
          <a href="javascript:void(0)" style={{marginLeft: '100px'}}>Meet The Team</a>
          <a href="https://github.com/AI-and-Blockchain/S23_PredictChain" style={{marginLeft: '100px'}}>Docs</a>
          <button className="dashboard__btn" onClick={logout}>
            Logout
          </button>
        </nav>       
      </div>
      <div className="dashboard">
        <div className="dashboard__container">
          Logged in as
          <div>{name}</div>
          <div>{user?.email}</div>
        </div>
      </div>
      <h1>Welcome {name}</h1>
      <div className="fixed-footer">
          <nav>
            <a href="javascript:void(0)" style={{fontSize: 'xx-large', fontWeight: '900', color: '#ffffff', marginRight: '80px', marginLeft: '100px'}}>PredictChain</a>
            <a href="javascript:void(0)"style={{marginLeft: '100px'}}>FAQ</a>
            <a href="javascript:void(0)" style={{marginLeft: '100px'}}>Meet The Team</a>
            <a href="https://github.com/AI-and-Blockchain/S23_PredictChain" style={{marginLeft: '100px'}}>Docs</a>
            <a href="#" style={{marginLeft: '100px'}}>Back to top</a>
          </nav>       
        </div>
    </div>
  );
}

export default Dashboard;