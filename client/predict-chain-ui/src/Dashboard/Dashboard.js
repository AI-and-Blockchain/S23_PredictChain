import React, { useEffect, useState } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { useNavigate } from "react-router-dom";
import { auth, db, logout } from "../firebase";
import {
  query,
  collection,
  getDoc,
  where,
  doc,
  updateDoc,
  arrayUnion
} from "firebase/firestore";
import axios from "axios";
import "./Dashboard.css";

function Dashboard() {
  // User information
  const [user, loading] = useAuthState(auth);
  const [name, setUserName] = useState("");
  const [pk, setPK] = useState("");
  const [addr, setAddr] = useState("");
  const [pastTxns, setPastTxns] = useState([]);

  const [datasetUploadPriceSize, setDatasetUploadPriceSize] = useState("");
  const [datasetUploadPrice, setDatasetUploadPrice] = useState(0);

  // Get Model Train Price function
  const [modelTrainNamePrice, setModelTrainNamePrice] = useState("");
  const [modelTrainDatasetNamePrice, setModelTrainDatasetNamePrice] = useState("");
  const [modelTrainPrice, setModelTrainPrice] = useState(0);

  // Get Model Query Price function
  const [queryPriceModelName, setQueryPriceModelName] = useState("");
  const [queryPriceModel, setQueryPriceModel] = useState(0);

  // Add dataset function
  const [addDatasetSize, setAddDatasetSize] = useState(0);
  const [addDatasetName, setAddDatasetName] = useState("");
  const [addDatasetLink, setAddDatasetLink] = useState("");

  // Train Model function
  const [trainRawModelName, setTrainRawModelName] = useState("");
  const [trainNewName, setTrainNewName] = useState("");
  const [trainDatasetName, setTrainDatasetName] = useState("");
  const [trainNumberEpochs, setTrainNumberEpochs] = useState("");


  const navigate = useNavigate();
  const fetchUserName = async () => {
    const docRef = doc(db, "users", user?.uid);
    const docSnap = await getDoc(docRef);

    setUserName(docSnap.data().name);
    setPK(docSnap.data().privateKey);
    setAddr(docSnap.data().address);
    setPastTxns(docSnap.data().transactionIDs);
  };


  const handleDatasetUploadPriceRequest = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8031/get_dataset_upload_price?ds_size=${datasetUploadPriceSize}`
      );
      setDatasetUploadPrice(response.data.price);
    } catch (error) {
      console.error(error);
      alert("Error fetching price");
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
        console.log(pastTxns);
        console.log(modelTrainDatasetNamePrice);
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

  const handleQueryModelPriceRequest = async () => {
      try {
        const response = await axios.get(`http://localhost:8031/get_model_query_price?trained_model=${queryPriceModelName}`);
        setQueryPriceModel(response.data.price);
      } catch (error) {
        console.error(error);
        alert("Error fetching price");
      }
    }


  const handleAddDataset = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post("http://localhost:8031/add_dataset", {
        ds_link: addDatasetLink,
        ds_name: addDatasetName,
        ds_size: addDatasetSize,
        time_attrib: "time_step",
      });
      setPastTxns([
        ...pastTxns,
        "Added Dataset (" + response.data + ") - " + addDatasetName
      ]);

      const userRef = doc(db, "users", user?.uid);
      await updateDoc(userRef, {
        transactionIDs: arrayUnion(
          "Added Dataset (" + response.data + ") - " + addDatasetName
        )
      });
    } catch (error) {
      console.error(error);
    }
  };

  const handleModelTraining = async (event) => { // next on agenda
    event.preventDefault();
    if (trainRawModelName == "--Select an option--" || trainRawModelName == ""){
      alert("Please select a model");
      return;
    }

    if (trainNewName == "" || trainDatasetName == ""){
      alert("Please enter a new trained model name/dataset name");
      return;
    }

    try {

      const containsWord = pastTxns.some(pastTxn => pastTxn.includes(trainDatasetName));
      if (!(containsWord)){
        alert("Cannot find dataset");
        return;
      }

      const response = await axios.post('http://localhost:8031/train_model', {
        raw_model: trainRawModelName,
        trained_model: trainNewName,
        ds_name: trainDatasetName,
        num_epochs: trainNumberEpochs,
        target_attrib: "close",
        hidden_dim: 5,
        num_hidden_layers: 1,
      });

      setPastTxns([...pastTxns, "Trained Dataset: '" + trainDatasetName + "' (" + response.data + ") - " + trainNewName]);
      // Get the user document reference
      const userRef = doc(db, "users", user?.uid);
      // Update the transaction IDs array with the new transaction ID
      await updateDoc(userRef, {
        transactionIDs: arrayUnion("Trained Dataset: '" + trainDatasetName + "' (" + response.data + ") - " + trainNewName)
      });
    } catch (error) {
      console.error(error);
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
          <a href="/faq"style={{marginLeft: '350px'}}>FAQ</a>
          <a href="/mtt" style={{marginLeft: '250px'}}>Meet The Team</a>
          <a href="http://localhost:8031/docs" style={{marginLeft: '200px'}}>Docs</a>
          <a href="https://github.com/AI-and-Blockchain/S23_PredictChain" target="_blank" style={{marginLeft: '200px'}}>GitHub</a>
        </nav>       
      </div>
      <div className="dashboard">
        <div className="dashboard__container">
          <h1 style={{textAlign: "left", marginLeft: "30px"}}>Welcome {name}!</h1>
          <h1 style={{textAlign: "left", marginLeft: "30px", color: "blue"}}>Account Info</h1>
          <div style={{display: "flex", alignItems: "center", textAlign: "left", marginLeft: "30px", marginTop: "-10px"}}>
            <h2 style={{marginRight: "10px", textDecoration: "underline"}}>Email:</h2>
            {user?.email}
          </div>
          <div style={{display: "flex", alignItems: "center", textAlign: "left", marginLeft: "30px",  marginTop: "-10px"}}>
            <h2 style={{marginRight: "10px", textDecoration: "underline"}}>Private Key:</h2>
            <div>{pk}</div>
          </div>
          <div style={{display: "flex", alignItems: "center", textAlign: "left", marginLeft: "30px",  marginTop: "-10px"}}>
            <h2 style={{marginRight: "10px", textDecoration: "underline"}}>Address:</h2>
            <div>{addr}</div>
          </div>

          <button className="dashboard__btn" onClick={logout}>Logout</button>
          
          
          <h1 style={{marginTop: "-375px", marginLeft: "950px", color: "blue"}}>Get Prices</h1>
          <div style={{zIndex: "1"}}>
            <div style={{marginLeft: "950px"}}>
                <h2 style={{textDecoration: "underline", marginTop: "10px"}}>Request Dataset Upload Price</h2>
                <div>
                    <input type="number" value={datasetUploadPriceSize} min="0" placeholder="0" onChange={(event) => setDatasetUploadPriceSize(event.target.value)}/>
                    <button style={{marginLeft: "10px"}} onClick={handleDatasetUploadPriceRequest}>Get Price</button>
                </div>
                {datasetUploadPrice >= 0 && (<div><h3 style={{marginTop: "-5px"}}>Price: {datasetUploadPrice}</h3></div>)}
            </div>
            <div style={{marginTop: "0px", marginLeft: "950px"}}>
                <h2 style={{textDecoration: "underline"}}>Request Model Train Price</h2>
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
                        <input style={{marginLeft: "10px"}} type="text" placeholder="Pre-existing dataset" value={modelTrainDatasetNamePrice} onChange={(e) => setModelTrainDatasetNamePrice(e.target.value)} />
                    </label>
                    <br/>
                    <button type="submit">Get Price</button>
                </form>
                {modelTrainPrice >= 0 && (<div><h3 style={{marginTop: "-5px"}}>Price: {modelTrainPrice}</h3></div>)}
            </div>
            <div style={{marginTop: "0px", marginLeft: "950px"}}>
                <h2 style={{textDecoration: "underline"}}>Request Model Query Price</h2>
                <div>
                    <input type="text" value={queryPriceModelName} placeholder="Pre-existing model" onChange={(event) => setQueryPriceModelName(event.target.value)}/>
                    <button style={{marginLeft: "10px"}} onClick={handleQueryModelPriceRequest}>Get Price</button>
                </div>
                {queryPriceModel >= 0 && (<div><h3 style={{marginTop: "-5px"}}>Price: {queryPriceModel}</h3></div>)}
            </div>
          </div>

          <h1 style={{marginLeft: "950px", color: "blue"}}>Dataset & Model Functions</h1>
          <div style={{marginLeft: "950px"}}>
            <h2 style={{textDecoration: "underline"}}>Add Dataset</h2>
            <form onSubmit={handleAddDataset}>
              <label style={{marginLeft: "10px"}}>
                Link to Dataset:
                <input style={{marginLeft: "10px"}} type="text" placeholder="Link to CSV" value={addDatasetLink} onChange={(e) => setAddDatasetLink(e.target.value)} />
              </label>
              <label style={{marginLeft: "10px"}}>
                New Dataset Name:
                <input style={{marginLeft: "10px"}} type="text" placeholder="Newly named dataset" value={addDatasetName} onChange={(e) => setAddDatasetName(e.target.value)} />
              </label>
              <br/>
              <label style={{marginLeft: "10px"}}>
                Dataset Size (bytes):
                <input  style={{marginLeft: "10px"}} type="number" min="0" placeholder="0" value={addDatasetSize} onChange={(e) => setAddDatasetSize(e.target.value)} />
              </label>
              <br/>
              <button type="submit">Add Dataset</button>
            </form>
          </div>

          <div style={{marginTop: "10px", marginLeft: "950px"}}>
            <h2 style={{textDecoration: "underline"}}>Train Model</h2>
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
                Trained Model Name:
                <input style={{marginLeft: "10px"}} type="text" placeholder="Newly named model" value={trainNewName} onChange={(e) => setTrainNewName(e.target.value)} />
              </label>
              <br/>
              <label style={{marginLeft: "10px"}}>
                Dataset Name:
                <input style={{marginLeft: "10px"}} type="text" placeholder="Pre-existing dataset" value={trainDatasetName} onChange={(e) => setTrainDatasetName(e.target.value)} />
              </label>
              <label style={{marginLeft: "10px"}}>
                Number of Epochs:
                <input style={{marginLeft: "10px"}} type="number" min="1" placeholder="1" value={trainNumberEpochs} onChange={(e) => setTrainNumberEpochs(e.target.value)} />
              </label>
              <br/>
              <button type="submit">Train Dataset</button>
            </form>
          </div>
          <div style={{textAlign: "left", marginLeft: "30px", marginTop: "-575px", zIndex: "0"}}><h2 style={{textDecoration: "underline"}}>Past Transactions:</h2>
            <ul>{pastTxns.map((item, index) => { return <li key={index}>{item}</li>;})}</ul>
          </div>
        </div>
      </div>
      <div className="fixed-footer">
        <nav>
          <a href="/" style={{fontSize: 'xx-large', fontWeight: '900', color: '#ffffff', marginRight: '80px', marginLeft: '100px'}}>PredictChain</a>
          <a href="/faq"style={{marginLeft: '300px'}}>FAQ</a>
          <a href="/mtt" style={{marginLeft: '200px'}}>Meet The Team</a>
          <a href="http://localhost:8031/docs" style={{marginLeft: '200px'}}>Docs</a>
          <a href="https://github.com/AI-and-Blockchain/S23_PredictChain" target="_blank" style={{marginLeft: '150px'}}>GitHub</a>
          <a href="#" style={{marginLeft: '150px'}}>Back to top</a>
        </nav> 
      </div>
    </div>
)};

export default Dashboard;