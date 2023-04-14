import React, { useEffect, useState } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { useNavigate } from "react-router-dom";
import {
  auth,
  registerWithEmailAndPassword,
  signInWithGoogle,
} from "../firebase";
import "./Register.css";

function Register() {
  const [email, setEmail] = useState(""); // set email
  const [password, setPassword] = useState(""); // set password
  const [name, setName] = useState(""); // set name
  const [user, loading] = useAuthState(auth); // authenticate
  const navigate = useNavigate(); // nav

  const register = () => {
    if (!name) alert("Please enter name");

    registerWithEmailAndPassword(name, email, password);
  };

  useEffect(() => {
    if (loading) return;
    if (user) navigate("/dashboard");
  }, [user, loading]);

  return (
    <div>
      <div className="header">
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
        </nav>
      </div>
      <div className="register">
        <div className="register__container">
          <h2 style={{ marginBottom: "40px" }}>Create Account</h2>
          <input
            type="text"
            className="register__textBox"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Full Name"
          />
          <input
            type="text"
            className="register__textBox"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="E-mail Address"
          />
          <input
            type="password"
            className="register__textBox"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
          />
          <button className="register__btn" onClick={register}>
            Register
          </button>
          <button
            className="register__btn register__google"
            onClick={signInWithGoogle}
          >
            Register with Google
          </button>

          <div>
            Already have an account?{" "}
            <a href="/login" className="ex1">
              Login
            </a>{" "}
            now.
          </div>
        </div>
      </div>
      <div className="footer">
        <nav>
          <a href="/faq">FAQ</a>
          <a href="/mtt" style={{ marginLeft: "100px" }}>
            Meet The Team
          </a>
          <a href="http://localhost:8031/docs" style={{ marginLeft: "100px" }}>
            Docs
          </a>
          <a
            href="https://github.com/AI-and-Blockchain/S23_PredictChain"
            target="_blank"
            style={{ marginLeft: "100px" }}
          >
            GitHub
          </a>
        </nav>
      </div>
    </div>
  );
}

export default Register;
