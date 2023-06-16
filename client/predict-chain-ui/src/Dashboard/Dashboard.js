import React, { useEffect, useState } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { useNavigate } from "react-router-dom";
import { auth, db, logout } from "../firebase";
import { getDoc, doc, updateDoc, arrayUnion } from "firebase/firestore";
import axios from "axios";
import "./Dashboard.css";

function Dashboard() {
  // User information
  const [user, loading] = useAuthState(auth);
  const [name, setUserName] = useState("");
  const [pk, setPK] = useState("");
  const [addr, setAddr] = useState("");
  const [dsState, setDsState] = useState([]);
  const [modelState, setModelState] = useState([]);
  const [pastTxns, setPastTxns] = useState([]);
  const [pastURLs, setPastURLs] = useState([]);
  const [incomingRespTxns, setIncomingRespTxns] = useState([]);

  const [datasetUploadPriceSize, setDatasetUploadPriceSize] = useState("");
  const [datasetUploadPrice, setDatasetUploadPrice] = useState(0);

  // Get Model Train Price function
  const [modelTrainNamePrice, setModelTrainNamePrice] = useState("");
  const [modelTrainDatasetNamePrice, setModelTrainDatasetNamePrice] =
    useState("");
  const [modelTrainPrice, setModelTrainPrice] = useState(0);

  // Get Model Query Price function
  const [queryPriceModelName, setQueryPriceModelName] = useState("");
  const [queryPriceModel, setQueryPriceModel] = useState(0);

  // Add dataset function
  const [addDatasetSize, setAddDatasetSize] = useState("");
  const [addDatasetName, setAddDatasetName] = useState("");
  const [addDatasetLink, setAddDatasetLink] = useState("");

  // Train Model function
  const [trainRawModelName, setTrainRawModelName] = useState("");
  const [trainNewName, setTrainNewName] = useState("");
  const [trainDatasetName, setTrainDatasetName] = useState("");
  const [trainNumberEpochs, setTrainNumberEpochs] = useState("");

  // Query Model function
  const [queryModelName, setQueryModelName] = useState("");
    const [queryModelData, setQueryModelData] = useState("");

  const navigate = useNavigate();
  const fetchUserName = async () => {
    const docRef = doc(db, "users", user?.uid);
    const docSnap = await getDoc(docRef);

    setUserName(docSnap.data().name);
    setPK(docSnap.data().privateKey);
    setAddr(docSnap.data().address);
    setPastTxns(docSnap.data().transactionIDs);
    setPastURLs(docSnap.data().urlList);
  };

  const fetchBackendState = async () => {
    let updates = [[], []];
    try {
      const ds_response = await axios.get(`http://localhost:8031/get_datasets`);
      for(let ds of Object.keys(ds_response.data))
        updates[0].push(ds.replace("<DS>", ""));

      const model_response = await axios.get(`http://localhost:8031/get_models`);
      for(let model of Object.keys(model_response.data))
        updates[1].push(model.replace("<MODEL>", ""));
    } catch (error) {
      console.error(error);
      alert("Error fetching backend state");
    }
    setDsState(updates[0]);
    setModelState(updates[1]);
  };

  const handleDatasetUploadPriceRequest = async () => {
    // get price for uploading a dataset
    try {
      const response = await axios.get(
        `http://localhost:8031/get_dataset_upload_price?ds_size=${datasetUploadPriceSize}`
      );
      setDatasetUploadPrice(response.data.price);
      setDatasetUploadPriceSize("");
    } catch (error) {
      console.error(error);
      alert("Error fetching price");
    }
  };

  const handleModelTrainPrice = async (event) => {
    // get price for training a model
    event.preventDefault();
    if (modelTrainNamePrice === "--Select an option--" || modelTrainNamePrice === "") {
      // edge case
      alert("Please select a model");
      return;
    }

    if (modelTrainDatasetNamePrice === "") {
      // edge case
      alert("Please enter a dataset name");
      return;
    }

    try {
      // Check if the dataset exists in the oracle's database
      if (!dsState.includes(modelTrainDatasetNamePrice)) {
        alert("Cannot find dataset");
        return;
      }
      // Get the model train price
      const response = await axios.get(
        `http://localhost:8031/get_model_train_price?raw_model=${modelTrainNamePrice}&ds_name=${modelTrainDatasetNamePrice}&hidden_dim=5&num_hidden_layers=1`
      );
      setModelTrainPrice(response.data.price);
      setModelTrainNamePrice("");
      setModelTrainDatasetNamePrice("");
    } catch (error) {
      console.error(error);
      alert("Error fetching price");
    }
  };

  const handleQueryModelPriceRequest = async () => {
    if (queryPriceModelName === "") {
      alert("Enter a model name!");
      return;
    }

    try {
      const response = await axios.get(
        `http://localhost:8031/get_model_query_price?trained_model=${queryPriceModelName}`
      );
      setQueryPriceModel(response.data.price);
      setQueryPriceModelName("");
    } catch (error) {
      console.error(error);
      alert("Error fetching price");
    }
  };

  const handleAddDataset = async (event) => {
    event.preventDefault();

    if (dsState.includes(addDatasetName)) {
      alert("Enter a different dataset name!");
      return;
    }
    try {
      const response = await axios.post("http://localhost:8031/add_dataset", {
        ds_link: addDatasetLink,
        ds_name: addDatasetName,
        ds_size: addDatasetSize,
        time_attrib: "time_step",
      });
      setPastTxns([...pastTxns, "Added Dataset: '" + addDatasetName + "' (TXN ID: ",]);

      const newURL = `https://testnet.algoexplorer.io/tx/${response.data}`;
      setPastURLs([...pastURLs, newURL]);

      const userRef = doc(db, "users", user?.uid);
      await updateDoc(userRef, {
        transactionIDs: arrayUnion("Added Dataset: '" + addDatasetName + "' (TXN ID: ",),
        urlList: arrayUnion(newURL)
      });
      setAddDatasetLink("");
      setAddDatasetName("");
      setAddDatasetSize("");
    } catch (error) {
      console.error(error);
    }
  };

  const handleModelTraining = async (event) => {
    // next on agenda
    event.preventDefault();
    if (
      trainRawModelName === "--Select an option--" ||
      trainRawModelName === ""
    ) {
      alert("Please select a model");
      return;
    }

    if (trainNewName === "" || trainDatasetName === "") {
      alert("Please enter a new trained model name/dataset name");
      return;
    }

    try {
      if (!dsState.includes(trainDatasetName)) {
        alert("Cannot find dataset");
        return;
      }

      const response = await axios.post("http://localhost:8031/train_model", {
        raw_model: trainRawModelName,
        trained_model: trainNewName,
        ds_name: trainDatasetName,
        num_epochs: trainNumberEpochs,
        target_attrib: "close",
        hidden_dim: 5,
        num_hidden_layers: 2,
      });

      setPastTxns([...pastTxns, "Trained Dataset: '" + trainDatasetName +
        "' to create '" + trainNewName + "' (TXN ID: ",]);

      const newURL = `https://testnet.algoexplorer.io/tx/${response.data}`;
      setPastURLs([...pastURLs, newURL]);
      // Get the user document reference
      const userRef = doc(db, "users", user?.uid);
      // Update the transaction IDs array with the new transaction ID
      await updateDoc(userRef, {
        transactionIDs: arrayUnion("Trained Dataset: '" + trainDatasetName +
            "' to create '" + trainNewName + "' (TXN ID: ",),
        urlList: arrayUnion(newURL)
      });
      setTrainRawModelName("");
      setTrainNewName("");
      setTrainDatasetName("");
      setTrainNumberEpochs("");
    } catch (error) {
      console.error(error);
    }
  };

  const handleQueryModel = async (event) => {
    // next on agenda
    event.preventDefault();
    if (queryModelName === "") {
      alert("Please enter a name");
      return;
    }
    if (queryModelData === "") {
      alert("Please enter some input");
      return;
    }

    try {
      if (!modelState.includes(queryModelName)) {
        alert("Cannot find model");
        return;
      }

      const response = await axios.post("http://localhost:8031/query_model", {
        trained_model: queryModelName,
        model_input: JSON.parse(queryModelData),
      });

      setPastTxns([...pastTxns, "Queried Model: '" + queryModelName + "' (TXN ID: ",]);

      const newURL = `https://testnet.algoexplorer.io/tx/${response.data}`;
      setPastURLs([...pastURLs, newURL]);
      // Get the user document reference
      const userRef = doc(db, "users", user?.uid);
      // Update the transaction IDs array with the new transaction ID
      await updateDoc(userRef, {
        transactionIDs: arrayUnion("Queried Model: '" + queryModelName + "' (TXN ID: ",),
        urlList: arrayUnion(newURL)
      });
      setQueryModelName("");
      setQueryModelData("");
    } catch (error) {
      console.error(error);
    }
  };

  const handleGetIncoming = async () => {
    const response = await axios.get("http://localhost:8031/incoming_transactions");
    //console.log("Incoming response", response.data);
    let tmp = [...incomingRespTxns, ...response.data];
    console.log("Tmp", tmp, incomingRespTxns);
    setIncomingRespTxns(tmp);
  };

  const mainLoop = async () => {
    while(true){
      fetchBackendState();
      // Not really reactive, but this gets rid of a lot of async state nonsense
      document.getElementById("getIncomingButton").click();
      await new Promise(r => setTimeout(r, 5000));
    }
  };

  useEffect(() => {
    if (loading) return;
    if (!user) return navigate("/");

    fetchUserName();
    mainLoop();
  }, [user, loading]);

  return (
    <div>
      <div className="fixed-header">
        <nav>
          <a
            href="/"
            style={{
              fontSize: "xx-large",
              fontWeight: "900",
              color: "#ffffff",
              marginRight: "80px",
              marginLeft: "100px",
            }}
          >
            PredictChain
          </a>
          <a href="/faq" style={{ marginLeft: "350px" }}>
            FAQ
          </a>
          <a href="/mtt" style={{ marginLeft: "250px" }}>
            Meet The Team
          </a>
          <a href="http://localhost:8031/docs" style={{ marginLeft: "200px" }}>
            Docs
          </a>
          <a
            href="https://github.com/AI-and-Blockchain/S23_PredictChain"
            target="_blank"
            style={{ marginLeft: "200px" }} rel="noreferrer"
          >
            GitHub
          </a>
        </nav>
      </div>
      <div className="dashboard">
        <div className="dashboard__container">
          <h1
            style={{
              textAlign: "left",
              marginLeft: "30px",
              color: "white",
              fontSize: "40px",
            }}
          >
            Welcome {name}!
          </h1>
          <h1 style={{ textAlign: "left", marginLeft: "30px" }}>
            Account Info
          </h1>
          <div className="credentials__txt">
            <h2
              style={{
                fontSize: "24px",
                marginRight: "10px",
                marginTop: "20px",
                textDecoration: "underline",
              }}
            >
              Email:
            </h2>
            {user?.email}
          </div>
          {/*<div className="credentials__txt">
            <h2 style={{ marginRight: "10px", textDecoration: "underline", marginTop: "20px"}}>
              Private Key:
            </h2>
            <div>{pk}</div>
          </div>*/}
          <div className="credentials__txt">
            <h2 style={{ marginRight: "10px", textDecoration: "underline", marginTop: "20px" }}>
              Address:
            </h2>
            <div>{addr}</div>
          </div>
          <div className="left-aligned" style={{maxWidth: "50%"}}>
            <p>Existing datasets: {JSON.stringify(dsState).replace(/"|\[|]/g, "")}</p>
            <br/>
            <p>Existing models: {JSON.stringify(modelState).replace(/"|\[|]/g, "")}</p>
          </div>
          <button className="dashboard__btn" onClick={logout}>
            Logout
          </button>

          <h1 style={{marginTop: "-600px", marginLeft: "950px",}}>
            Get Prices
          </h1>
          <div style={{ zIndex: "1" }}>
            <div style={{ marginLeft: "950px" }}>
              <h2 style={{ textDecoration: "underline", marginTop: "-10px" }}>
                Request Dataset Upload Price
              </h2>
              <div>
                <input
                  style={{ marginLeft: "-100px" }}
                  type="number"
                  value={datasetUploadPriceSize}
                  min="0"
                  placeholder="dataset size"
                  onChange={(event) =>
                    setDatasetUploadPriceSize(event.target.value)
                  }
                />
                <button
                  className="regular__btn"
                  style={{ marginLeft: "0px" }}
                  onClick={handleDatasetUploadPriceRequest}
                >
                  Get Price
                </button>
              </div>
              {datasetUploadPrice >= 0 && (
                <div>
                  <h3 style={{ marginTop: "-5px" }}>
                    Price: {datasetUploadPrice} Algo
                  </h3>
                </div>
              )}
            </div>
            <div style={{ marginTop: "0px", marginLeft: "950px" }}>
              <h2 style={{ textDecoration: "underline" }}>
                Request Model Train Price
              </h2>
              <form onSubmit={handleModelTrainPrice}>
                <label style={{ marginLeft: "10px" }}>
                  Model Type:
                  <select
                    style={{ marginLeft: "10px" }}
                    value={modelTrainNamePrice}
                    onChange={(e) => setModelTrainNamePrice(e.target.value)}
                  >
                    <option value="">--Select an option--</option>
                    <option value="GRU">Gated Recurrent Unit (GRU)</option>
                    <option value="LSTM">Long Short-Term Memory (LSTM)</option>
                    <option value="RNN">Recurrent Neural Network (RNN)</option>
                    <option value="MLP">Multi-Layered Perceptron (MLP)</option>
                  </select>
                </label>
                <label style={{ marginLeft: "10px" }}>
                  Dataset Name:
                  <select
                    style={{ marginLeft: "10px" }}
                    value={modelTrainDatasetNamePrice}
                    onChange={(e) => setModelTrainDatasetNamePrice(e.target.value)}
                  >
                    <option value="">--Select an option--</option>
                    {dsState.map((item,index)=>{
                        return <option key={index} value={item}>{item}</option>
                    })}
                  </select>
                </label>
                <br />
                <button
                  className="regular__btn"
                  style={{ marginTop: "5px", marginLeft: "-70px" }}
                >
                  Get Price
                </button>
              </form>
              <br />
              {modelTrainPrice >= 0 && (
                <div>
                  <h3 style={{ marginTop: "5px" }}>Price: {modelTrainPrice} Algo</h3>
                </div>
              )}
            </div>
            <div style={{ marginTop: "0px", marginLeft: "950px" }}>
              <h2 style={{ textDecoration: "underline" }}>
                Request Model Query Price
              </h2>
              <div>
                <label style={{ marginLeft: "10px" }}>
                Trained Model Name:
                  <select
                      style={{ marginLeft: "10px" }}
                      value={queryPriceModelName}
                      onChange={(e) => setQueryPriceModelName(e.target.value)}
                    >
                      <option value="">--Select an option--</option>
                      {modelState.map((item,index)=>{
                          return <option key={index} value={item}>{item}</option>
                      })}
                  </select>
                </label>
                <button
                  className="regular__btn"
                  style={{ marginLeft: "0px" }}
                  onClick={handleQueryModelPriceRequest}
                >
                  Get Price
                </button>
              </div>
              {queryPriceModel >= 0 && (
                <div>
                  <h3 style={{ marginTop: "-5px"}}>
                    Price: {queryPriceModel} Algo
                  </h3>
                </div>
              )}
            </div>
          </div>

          <h1 style={{ marginLeft: "950px" }}>
            Dataset & Model Functions
          </h1>
          <div style={{ marginLeft: "950px" }}>
            <h2 style={{ marginTop: "-10px", textDecoration: "underline" }}>
              Add Dataset
            </h2>
            <form onSubmit={handleAddDataset}>
              <label style={{ marginLeft: "10px" }}>
                Link to Dataset:
                <input
                  style={{ marginLeft: "10px" }}
                  type="text"
                  placeholder="Link to CSV"
                  value={addDatasetLink}
                  onChange={(e) => setAddDatasetLink(e.target.value)}
                />
              </label>
              <br/>
              <label style={{ marginLeft: "10px" }}>
                New Dataset Name:
                <input
                  style={{ marginLeft: "10px" }}
                  type="text"
                  placeholder="Newly named dataset"
                  value={addDatasetName}
                  onChange={(e) => setAddDatasetName(e.target.value)}
                />
              </label>
              <br />
              <label style={{ marginLeft: "10px" }}>
                Dataset Size (bytes):
                <input
                  style={{ marginLeft: "10px" }}
                  type="number"
                  min="0"
                  placeholder="0"
                  value={addDatasetSize}
                  onChange={(e) => setAddDatasetSize(e.target.value)}
                />
              </label>
              <br />
              <button
                type="submit"
                className="regular__btn"
                style={{ marginTop: "10px", marginLeft: "-70px" }}
              >
                Add Dataset
              </button>
            </form>
          </div>

          <div style={{ marginTop: "30px", marginLeft: "950px" }}>
            <h2 style={{ textDecoration: "underline" }}>Train Dataset</h2>
            <form onSubmit={handleModelTraining}>
              <label style={{ marginLeft: "10px" }}>
                Model Type:
                <select
                  style={{ marginLeft: "10px" }}
                  value={trainRawModelName}
                  onChange={(e) => setTrainRawModelName(e.target.value)}
                >
                  <option value="">--Select an option--</option>
                  <option value="GRU">Gated Recurrent Unit (GRU)</option>
                  <option value="LSTM">Long Short-Term Memory (LSTM)</option>
                  <option value="RNN">Recurrent Neural Network (RNN)</option>
                  <option value="MLP">Multi-Layered Perceptron (MLP)</option>
                </select>
              </label>
              <label style={{ marginLeft: "10px" }}>
                Trained Model Name:
                <input
                  style={{ marginLeft: "10px" }}
                  type="text"
                  placeholder="Newly named model"
                  value={trainNewName}
                  onChange={(e) => setTrainNewName(e.target.value)}
                />
              </label>
              <br />
              <label style={{ marginLeft: "10px" }}>
                Dataset Name:
                <select
                      style={{ marginLeft: "10px" }}
                      value={trainDatasetName}
                      onChange={(e) => setTrainDatasetName(e.target.value)}
                    >
                      <option value="">--Select an option--</option>
                      {dsState.map((item,index)=>{
                          return <option key={index} value={item}>{item}</option>
                      })}
                  </select>
              </label>
              <label style={{ marginLeft: "10px" }}>
                Number of Epochs:
                <input
                  style={{ marginLeft: "10px" }}
                  type="number"
                  min="1"
                  placeholder="1"
                  value={trainNumberEpochs}
                  onChange={(e) => setTrainNumberEpochs(e.target.value)}
                />
              </label>
              <br />
              <button
                type="submit"
                className="regular__btn"
                style={{ marginTop: "10px", marginLeft: "-70px" }}
              >
                Train Dataset
              </button>
            </form>
            <br/>
            <br/>
          </div>

          <div style={{ marginTop: "30px", marginLeft: "950px" }}>
            <h2 style={{ textDecoration: "underline" }}>Query Model</h2>
            <form onSubmit={handleQueryModel}>
              <label style={{ marginLeft: "10px" }}>
                Trained Model Name:
                <select
                    style={{ marginLeft: "10px" }}
                    value={queryModelName}
                    onChange={(e) => setQueryModelName(e.target.value)}
                  >
                    <option value="">--Select an option--</option>
                    {modelState.map((item,index)=>{
                        return <option key={index} value={item}>{item}</option>
                    })}
                </select>
              </label>
              <br/>
              <label style={{ marginLeft: "10px" }}>
                Query Input:
                <input
                  style={{ marginLeft: "10px" }}
                  type="text"
                  placeholder="JSON-encoded input"
                  value={queryModelData}
                  onChange={(e) => setQueryModelData(e.target.value)}
                />
              </label>
              <br />
              <button
                type="submit"
                className="regular__btn"
                style={{ marginTop: "10px", marginLeft: "-70px" }}
              >
                Query Model
              </button>
            </form>
          </div>
          <div
            style={{
              textAlign: "left",
              marginLeft: "30px",
              marginTop: "-470px",
              maxWidth: "50%"
            }}
          >
            <h2 style={{ fontSize: "24px", textDecoration: "underline" }}>
              Past Transaction(s):
            </h2>
            <ul>
            {pastTxns.map((item, index) => {
              const url = pastURLs[index];
              const urlText = url ? `${url.substring(url.length - 52)}` : "";
              return (
                <li key={index} style={{ fontSize: "16px" }}>
                  {item} <a className="urllist" target="_blank" href={url}>{urlText}</a>)
                </li>
              );
            })}
            </ul>
            <br/>

            <button id="getIncomingButton" style={{visibility: "hidden"}} onClick={handleGetIncoming}>Manually Get Incoming Responses</button>
            <br/>
            <label>
              Transaction Responses:
              <ul style={{minHeight: "10px", borderStyle: "solid"}}>{incomingRespTxns.map((txn) => {
                let filtered = {}
                for(let key of Object.keys(txn["note"]))
                  if(!key.includes("op"))
                    filtered[key] = txn["note"][key]
                return <li key={txn["id"]}>
                  Response for: {txn["note"]["initial_op"]}, Details: {JSON.stringify(filtered)}
                </li>})}</ul>
            </label>

          </div>
        </div>
      </div>
      <div className="fixed-footer">
        <nav>
          <a
            href="/"
            style={{
              fontSize: "xx-large",
              fontWeight: "900",
              color: "#ffffff",
              marginRight: "80px",
              marginLeft: "100px",
            }}
          >
            PredictChain
          </a>
          <a href="/faq" style={{ marginLeft: "300px" }}>
            FAQ
          </a>
          <a href="/mtt" style={{ marginLeft: "200px" }}>
            Meet The Team
          </a>
          <a href="http://localhost:8031/docs" style={{ marginLeft: "200px" }}>
            Docs
          </a>
          <a
            href="https://github.com/AI-and-Blockchain/S23_PredictChain"
            target="_blank"
            style={{ marginLeft: "150px" }} rel="noreferrer"
          >
            GitHub
          </a>
          <a href="#" style={{ marginLeft: "150px" }}>
            Back to top
          </a>
        </nav>
      </div>
    </div>
  );
}

export default Dashboard;
