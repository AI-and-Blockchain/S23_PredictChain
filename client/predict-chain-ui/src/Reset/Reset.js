import React, { useEffect, useState } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { useNavigate } from "react-router-dom";
import { auth, sendPasswordReset } from "../firebase";
import "./Reset.css";

function Reset() {
  const [email, setEmail] = useState("");
  const [user, loading] = useAuthState(auth);
  const navigate = useNavigate();

  const handleSendPassword = async (email) => {
    await sendPasswordReset(email);
    setEmail("");
  };

  useEffect(() => {
    if (loading) return;
    if (user) navigate("/dashboard");
  }, [user, loading]);

  return (
    <div className="reset">
      <div className="reset__container">
        <input
          type="text"
          className="reset__textBox"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="E-mail Address"
        />
        <button
          className="reset__btn"
          onClick={() => handleSendPassword(email)}
        >
          Send password reset email
        </button>

        <div>
          Don't have an account?{" "}
          <a href="/register" className="ex1">
            Register
          </a>{" "}
          now.
        </div>
      </div>
    </div>
  );
}

export default Reset;
