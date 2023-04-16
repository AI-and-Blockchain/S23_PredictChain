import "./Footer.css";

function Footer() {
  return (
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
        <a
          href="/register"
          style={{ fontSize: "x-large", marginLeft: "150px" }}
        >
          Create Account
        </a>
        <a href="/login" style={{ fontSize: "x-large", marginLeft: "100px" }}>
          Login
        </a>
        <a href="/faq" style={{ fontSize: "x-large", marginLeft: "100px" }}>
          FAQ
        </a>
        <a href="/mtt" style={{ fontSize: "x-large", marginLeft: "100px" }}>
          Meet The Team
        </a>
        <a
          href="http://localhost:8031/docs"
          target="_blank"
          style={{ fontSize: "x-large", marginLeft: "100px" }} rel="noreferrer"
        >
          Docs
        </a>
        <a
          href="https://github.com/AI-and-Blockchain/S23_PredictChain"
          target="_blank"
          style={{ fontSize: "x-large", marginLeft: "100px" }} rel="noreferrer"
        >
          GitHub
        </a>
        <a href="#" style={{ fontSize: "x-large", marginLeft: "100px" }}>
          Back to top
        </a>
      </nav>
    </div>
  );
}

export default Footer;
