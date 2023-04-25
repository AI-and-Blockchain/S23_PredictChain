import Header from "../Header/Header";
import Footer from "../Footer/Footer";
import "./MTT.css";
function MTT() {
  return (
    <div>
      <Header />
      <h1
        style={{
          textAlign: "center",
          fontSize: "56px",
          textDecoration: "underline",
        }}
      >
        Meet The Team!
      </h1>
      <br />
      <div class="row">
        <div class="column">
          <div class="card">
            <img
              src={require("../img/blank-prof.png")}
              alt="Jane"
              style={{ width: "80%" }}
            />
            <div class="container">
            </div>
          </div>
        </div>

        <div class="column">
          <div class="card">
            <img
              src={require("../img/blank-prof.png")}
              alt="Mike"
              style={{ width: "80%" }}
            />
            <div class="container">

            </div>
          </div>
        </div>

        <div class="column">
          <div class="card">
            <img
              src={require("../img/blank-prof.png")}
              alt="John"
              style={{ width: "80%" }}
            />
            <div class="container">
            </div>
          </div>
        </div>
      </div>
      <br />
      <br />
      <br />
      <Footer />
    </div>
  );
}
export default MTT;
