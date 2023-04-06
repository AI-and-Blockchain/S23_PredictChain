import React, { useState } from 'react';
import axios from 'axios';

const Testing = () => {
  const [response, setResponse] = useState(null);
  const [address, setAddr] = useState('');
  const [privateKey, setPK] = useState('');

  const handleClick = () => {
    axios.post('http://localhost:8031/new_account')
      .then(response => {
        setResponse(response);
        setAddr(response.data.address);
        setPK(response.data.private_key);
      });
  }

  return (
    <div>
      <button onClick={handleClick}>Click me</button>
      {address && <p>Address: {address}</p>}
      {privateKey && <p>Private Key: {privateKey}</p>}
    </div>
  );
};

export default Testing;
