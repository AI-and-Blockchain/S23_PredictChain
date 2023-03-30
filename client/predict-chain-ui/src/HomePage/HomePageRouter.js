import React from 'react';
import { BrowserRouter as Router, Routes, Route }
  from 'react-router-dom';
import HomePage from './HomePage';
import RegistrationForm from '../Registration/Registration';


function HomePageRouter() {
  return ( // usage of many components defined elsewhere, example of singleton pattern
    <div>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/create" element={<RegistrationForm />} /> 
        </Routes>
      </Router>
    </div>
  );
}

export default HomePageRouter;