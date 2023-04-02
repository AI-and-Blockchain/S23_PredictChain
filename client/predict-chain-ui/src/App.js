import "./App.css";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Register from "./Register/Register";
import Login from "./Login/Login";
import Dashboard from "./Dashboard/Dashboard";
import HomePage from "./HomePage/HomePage";
import Reset from "./Reset/Reset"
import MTT from "./MTT/MTT";
import FAQ from "./FAQ/FAQ";

function App() {
  return (
    <div className="app">
      <Router>
        <Routes>
          <Route exact path="/" element={<HomePage />} />
          <Route exact path="/login" element={<Login />} />
          <Route exact path="/register" element={<Register />} />
          <Route exact path="/reset" element={<Reset />} />
          <Route exact path="/dashboard" element={<Dashboard />} />
          <Route exact path="/mtt" element={<MTT />} />
          <Route exact path="/faq" element={<FAQ />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;