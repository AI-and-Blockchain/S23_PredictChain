import React, { useEffect, useState } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { useNavigate } from "react-router-dom";
import { auth, db, logout } from "../firebase";
import { query, collection, getDocs, where } from "firebase/firestore";
import axios from "axios";
import "./Dashboard.css";

function Dashboard() {
  const [user, loading] = useAuthState(auth); // used for fetching user
  const [name, setName] = useState(""); // used for setting name for dashboard
  const [pk, setPK] = useState(""); // private key
  const [addr, setAddr] = useState(""); // address
  const [transactions, setTransactions] = useState([]); // set transaction list
  const [datasetSize, setDatasetSize] = useState(""); // set templated data set size
  const [uploadPrice, setUploadPrice] = useState(0); // set templated upload price 
  const [size, setSize] = useState(0);
  const [datasetName, setDatasetName] = useState("");
  const [link, setLink] = useState("");
  const [transactionId, setTransactionId] = useState('');
  const navigate = useNavigate(); // for useEffect

  const handleUpdateState = () => { // this doesnt do much now
    axios.get('http://localhost:8031/update_state')
      .then(response => {setTransactions(response.data.transactions);})
      .catch(error => console.error(error));
  }

  const fetchUserName = async () => { // fetch username and other params
      const q = query(collection(db, "users"), where("uid", "==", user?.uid));
      const doc = await getDocs(q);
      const data = doc.docs[0].data();
      setName(data.name);
      setPK(data.privateKey);
      setAddr(data.address);
  };


  const handleAddDataset = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.get('http://localhost:8031/add_dataset', {
        params: {
          ds_link: link,
          ds_name: name,
          ds_size: size,
          time_attrib: "time_step"
        }
      });
      setTransactionId(response.data); // assuming the response is just the transaction ID
    } catch (error) {
      console.error(error);
    }
  };

  const handleDatasetUploadPriceRequest = async () => { // handles upload price request based on dataset size
    if(!datasetSize) {
      alert("Please enter a number");
    } else if (datasetSize >= 0) {
      try {
        const response = await axios.get(
          `http://localhost:8031/get_dataset_upload_price?ds_size=${datasetSize}`
        );
        setUploadPrice(response.data.price);
      } catch (error) {
        console.error(error);
        alert("Error fetching price");
      }
    } else {
      alert("Please enter a positive number");
    }
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
          <div style={{textAlign: "left", marginLeft: "50px"}}><h2>Email</h2>{user?.email}</div>
          <div style={{textAlign: "left", marginLeft: "50px"}}><h2>Private Key</h2> {pk}</div>
          <div style={{textAlign: "left", marginLeft: "50px"}}><h2>Address</h2> {addr}</div>
          <button className="dashboard__btn" onClick={logout}>
            Logout
          </button>
          <div style={{marginTop: "-400px", marginLeft: "950px"}}>
            <h2>Request Dataset Upload Price</h2>
            <div>
              <input
                type="number"
                value={datasetSize}
                min="0"
                onChange={(event) => setDatasetSize(event.target.value)}
              />
              <button onClick={handleDatasetUploadPriceRequest}>
                Get Price
              </button>
            </div>
            {uploadPrice >= 0 && (
              <div>
                <h3>Price: {uploadPrice}</h3>
              </div>
            )}
          </div>
          <div style={{marginLeft: "950px"}}>
            <h2>Add Dataset</h2>
            <form onSubmit={handleAddDataset}>
              <label style={{marginLeft: "10px"}}>
                Link:
                <input style={{marginLeft: "10px"}} type="text" value={link} onChange={(e) => setLink(e.target.value)} />
              </label>
              <label style={{marginLeft: "10px"}}>
                Name:
                <input style={{marginLeft: "10px"}} type="text" value={datasetName} onChange={(e) => setDatasetName(e.target.value)} />
              </label>
              <label style={{marginLeft: "10px"}}>
                Dataset Size (bytes):
                <input  style={{marginLeft: "10px"}} type="text" value={size} onChange={(e) => setSize(e.target.value)} />
              </label>
              <br/>
              <button type="submit">Submit</button>
            </form>
            {transactionId && <p>Oracle Transaction ID: {transactionId}</p>}
          </div>
          <div style={{marginTop: "500px"}}>
            <button onClick={handleUpdateState}>Update State</button>
            <ul>
              {transactions.map((txn, index) => (
                <li key={index}>{txn}</li>
              ))}
            </ul>
          </div>
        </div>
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
)};

export default Dashboard;