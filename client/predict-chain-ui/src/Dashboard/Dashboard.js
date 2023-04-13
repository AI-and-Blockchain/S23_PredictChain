import React, { useEffect, useState } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { useNavigate } from "react-router-dom";
import { auth, db, logout } from "../firebase";
import { query, collection, getDoc, where, doc, updateDoc, arrayUnion } from "firebase/firestore";
import axios from "axios";
import "./Dashboard.css";

function Dashboard() {
  // User information
  const [user, loading] = useAuthState(auth); // used for fetching user
  const [name, setUserName] = useState(""); // used for setting name for dashboard
  const [pk, setPK] = useState(""); // private key
  const [addr, setAddr] = useState(""); // address
  const [pastTxns, setPastTxns] = useState([]);

  // Get price for Dataset Size upload function 
  const [datasetUploadPriceSize, setDatasetUploadPriceSize] = useState(""); // set templated data set size
  const [datasetUploadPrice, setDatasetUploadPrice] = useState(0); // set templated upload price 
  
  // Add dataset function
  const [addDatasetSize, ssetAddDatasetSize] = useState(0);
  const [addDatasetName, setAddDatasetName] = useState("");
  const [addDatasetLink, setAddDatasetLink] = useState("");

  // Get Model Train Price function
  const [modelTrainNamePrice, setModelTrainNamePrice] = useState("");
  const [modelTrainDatasetNamePrice, setModelTrainDatasetNamePrice] = useState("");
  const [modelTrainPrice, setModelTrainPrice] = useState(0);

  // Train Model function
  const [trainRawModelName, setTrainRawModelName] = useState("");
  const [trainNewName, setTrainNewName] = useState("");
  const [trainDatasetName, setTrainDatasetName] = useState("");
  const [trainNumberEpochs, setTrainNumberEpochs] = useState("");

  const navigate = useNavigate(); // for useEffect
  const fetchUserName = async () => { // fetch username and other params
    const docRef = doc(db, "users", user?.uid);
    const docSnap = await getDoc(docRef);

    // set user info
    setUserName(docSnap.data().name);
    setPK(docSnap.data().privateKey);
    setAddr(docSnap.data().address);
    setPastTxns(docSnap.data().transactionIDs);
  };

  const handleDatasetUploadPriceRequest = async () => { // handles upload price request based on dataset size
    try {
      const response = await axios.get(`http://localhost:8031/get_dataset_upload_price?ds_size=${datasetUploadPriceSize}`);
      setDatasetUploadPrice(response.data.price);
    } catch (error) {
      console.error(error);
      alert("Error fetching price");
    }
  };


  const handleAddDataset = async (event) => { // add dataset
    event.preventDefault();
    try {
      const response = await axios.post('http://localhost:8031/add_dataset', {
        ds_link: addDatasetLink,
        ds_name: addDatasetName,
        ds_size: addDatasetSize,
        time_attrib: "time_step"
      });
      setPastTxns([...pastTxns, "Added Dataset (" + response.data + ") - " + addDatasetName]);
      
      // Get the user document reference
      const userRef = doc(db, "users", user?.uid);
      // Update the transaction IDs array with the new transaction ID
      await updateDoc(userRef, {
        transactionIDs: arrayUnion("Added Dataset (" + response.data + ") - " + addDatasetName)
      });
    } catch (error) {
      console.error(error);
    }
  };

  const handleModelTrainPrice = async (event) => {
    event.preventDefault();
    if (modelTrainNamePrice == "--Select an option--" || modelTrainNamePrice == "") { // edge case
      alert("Please select a model");
      return;
    }

    if (modelTrainDatasetNamePrice == "") { // edge case
      alert("Please enter a dataset name");
      return;
    }

    try {
      // Check if any of the past transactions have the dataset name
      const containsWord = pastTxns.some(pastTxn => pastTxn.includes(modelTrainDatasetNamePrice));

      if (!(containsWord)){
        alert("Cannot find dataset");
        return;
      }
      // Get the model train price
      const response = await axios.get(`http://localhost:8031/get_model_train_price?raw_model=${modelTrainNamePrice}&ds_name=${modelTrainDatasetNamePrice}&hidden_dim=5&num_hidden_layers=1`);
      setModelTrainPrice(response.data.price);
    } catch (error) {
      console.error(error);
      alert("Error fetching price");
    }
  };

  const handleModelTraining = async (event) => { // next on agenda
    event.preventDefault();

    console.log(trainRawModelName, trainNewName, trainDatasetName, trainNumberEpochs);
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
          <h1 style={{textAlign: "left", marginLeft: "30px"}}>Welcome {name}!</h1>
          <div style={{textAlign: "left", marginLeft: "30px"}}><h2>Email:</h2>{user?.email}</div>
          <div style={{textAlign: "left", marginLeft: "30px"}}><h2>Private Key:</h2> {pk}</div>
          <div style={{textAlign: "left", marginLeft: "30px"}}><h2>Address:</h2> {addr}</div>
          <div style={{textAlign: "left", marginLeft: "30px", marginTop: "40px"}}><h2>Past Transactions:</h2>
            <ul>{pastTxns.map((item, index) => { return <li key={index}>{item}</li>;})}</ul>
          </div>
          <button className="dashboard__btn" onClick={logout}>Logout</button>
          <div style={{marginTop: "-600px", marginLeft: "950px"}}>
            <h2>Request Dataset Upload Price</h2>
            <div>
              <input type="number" value={datasetUploadPriceSize} min="0" onChange={(event) => setDatasetUploadPriceSize(event.target.value)}/>
              <button onClick={handleDatasetUploadPriceRequest}>Get Price</button>
            </div>
            {datasetUploadPrice >= 0 && (<div><h3>Price: {datasetUploadPrice}</h3></div>)}
          </div>
          <div style={{marginLeft: "950px"}}>
            <h2>Add Dataset</h2>
            <form onSubmit={handleAddDataset}>
              <label style={{marginLeft: "10px"}}>
                Link to Dataset:
                <input style={{marginLeft: "10px"}} type="text" value={addDatasetLink} onChange={(e) => setAddDatasetLink(e.target.value)} />
              </label>
              <label style={{marginLeft: "10px"}}>
                New Dataset Name:
                <input style={{marginLeft: "10px"}} type="text" value={addDatasetName} onChange={(e) => setAddDatasetName(e.target.value)} />
              </label>
              <br/>
              <label style={{marginLeft: "10px"}}>
                Dataset Size (bytes):
                <input  style={{marginLeft: "10px"}} type="number" value={addDatasetSize} min="0" onChange={(e) => ssetAddDatasetSize(e.target.value)} />
              </label>
              <br/>
              <button type="submit">Submit</button>
            </form>
          </div>
          <div style={{marginTop: "50px", marginLeft: "950px"}}>
            <h2>Get Model Train Price</h2>
            <form onSubmit={handleModelTrainPrice}>
              <label style={{marginLeft: "10px"}}>
                Model Name:
                <select style={{marginLeft: "10px"}} value={modelTrainNamePrice} onChange={(e) => setModelTrainNamePrice(e.target.value)}>
                  <option value="">--Select an option--</option>
                  <option value="GRU">Gated Recurrent Unit (GRU)</option>
                  <option value="LSTM">Long Short-Term Memory (LSTM)</option>
                  <option value="RNN">Recurrent Neural Network (RNN)</option>
                  <option value="MLP">Multi-Layered Perceptron (MLP)</option>
                </select>
              </label>
              <label style={{marginLeft: "10px"}}>
                Dataset Name:
                <input style={{marginLeft: "10px"}} type="text" value={modelTrainDatasetNamePrice} onChange={(e) => setModelTrainDatasetNamePrice(e.target.value)} />
              </label>
              <br/>
              <button type="submit">Submit</button>
            </form>
            {modelTrainPrice >= 0 && (<div><h3>Price: {modelTrainPrice}</h3></div>)}
          </div>
          <div style={{marginTop: "50px", marginLeft: "950px"}}>
            <h2>Train Model</h2>
            <form onSubmit={handleModelTraining}>
              <label style={{marginLeft: "10px"}}>
                Model Name:
                  <select style={{marginLeft: "10px"}} value={trainRawModelName} onChange={(e) => setTrainRawModelName(e.target.value)}>
                    <option value="">--Select an option--</option>
                    <option value="GRU">Gated Recurrent Unit (GRU)</option>
                    <option value="LSTM">Long Short-Term Memory (LSTM)</option>
                    <option value="RNN">Recurrent Neural Network (RNN)</option>
                    <option value="MLP">Multi-Layered Perceptron (MLP)</option>
                  </select>
              </label>
              <label style={{marginLeft: "10px"}}>
                New Trained Model Name:
                <input style={{marginLeft: "10px"}} type="text" value={trainNewName} onChange={(e) => setTrainNewName(e.target.value)} />
              </label>
              <br/>
              <label style={{marginLeft: "10px"}}>
                Dataset Name:
                <input style={{marginLeft: "10px"}} type="text" value={trainDatasetName} onChange={(e) => setTrainDatasetName(e.target.value)} />
              </label>
              <label style={{marginLeft: "10px"}}>
                Number of Epochs:
                <input style={{marginLeft: "10px"}} type="number" min="1" value={trainNumberEpochs} onChange={(e) => setTrainNumberEpochs(e.target.value)} />
              </label>
              <br/>
              <button type="submit">Submit</button>
            </form>
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