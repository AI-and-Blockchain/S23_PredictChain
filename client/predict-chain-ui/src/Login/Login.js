import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { auth, logInWithEmailAndPassword, signInWithGoogle } from "../firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import "./Login.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, loading, error] = useAuthState(auth);
  const navigate = useNavigate();

  useEffect(() => { 
    if (loading) {
      // maybe trigger a loading screen
      return;
    }
    if (user) navigate("/dashboard");
  }, [user, loading]);

  return (
    <div>
      <div className="header">
        <nav>
          <a href="/" style={{fontSize: 'xx-large', fontWeight: '900', color: '#ffffff', marginRight: '80px', marginLeft: '100px'}}>PredictChain</a>
        </nav>  
      </div>
      <div className="login">
        <div className="login__container">
          <h2>Login</h2>
          <input
            type="text"
            className="login__textBox"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="E-mail Address"
          />
          <input
            type="password"
            className="login__textBox"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
          />
          <button
            className="login__btn"
            onClick={() => logInWithEmailAndPassword(email, password)}
          >
            Login
          </button>
          <button className="login__btn login__google" onClick={signInWithGoogle}>
            Login with Google
          </button>
          <div>
            <a href="/reset" className="ex1">Forgot Password</a>
          </div>
          <div>
            Don't have an account? <a href="/register" className="ex1">Register</a> now.
          </div>
        </div>
      </div>
      <div className="footer">
        <nav>
          <a href="/faq">FAQ</a>
          <a href="/mtt" style={{marginLeft: '100px'}}>Meet The Team</a>
          <a href="http://localhost:8031/docs" style={{marginLeft: '100px'}}>Docs</a>
          <a href="https://github.com/AI-and-Blockchain/S23_PredictChain" target="_blank" style={{marginLeft: '100px'}}>GitHub</a>

        </nav>       
      </div>
    </div>
  );
}

export default Login;