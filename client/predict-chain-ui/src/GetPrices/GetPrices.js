// DatasetUpload.js
import React, { useEffect, useState } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { useNavigate } from "react-router-dom";
import { auth, db } from "../firebase";
import {
  getDoc,
  doc,
} from "firebase/firestore";
import axios from "axios";

function GetPrices() {
    const [user, loading] = useAuthState(auth);
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


    const navigate = useNavigate();
    const fetchUserName = async () => {
      const docRef = doc(db, "users", user?.uid);
      const docSnap = await getDoc(docRef);
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

    useEffect(() => {
      if (loading) return;
      if (!user) return navigate("/");
      
      fetchUserName();
    }, [user, loading]);

    return (
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
  );
}

export default GetPrices;
