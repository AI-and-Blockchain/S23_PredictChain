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
              src={require("../img/image-src.png")}
              alt="Jane"
              style={{ width: "80%" }}
            />
            <div class="container">
              <h2>William Hawkins</h2>
              <p class="title">Group Member</p>
              <p>Graduate CS student @ RPI</p>
              <p>BIO HERE</p>
              <p>
                <button class="button">
                  <a href="mailto:hawkiw2@rpi.edu">Contact</a>
                </button>
              </p>
            </div>
          </div>
        </div>

        <div class="column">
          <div class="card">
            <img
              src={require("../img/image-src.png")}
              alt="Mike"
              style={{ width: "80%" }}
            />
            <div class="container">
              <h2>Connor Patterson</h2>
              <p class="title">Group Member</p>
              <p>Undergraduate CS student @ RPI</p>
              <p>BIO HERE</p>
              <p>
                <button class="button">
                  <a href="mailto:pattec3@rpi.edu">Contact</a>
                </button>
              </p>
            </div>
          </div>
        </div>

        <div class="column">
          <div class="card">
            <img
              src={require("../img/image-src.png")}
              alt="John"
              style={{ width: "80%" }}
            />
            <div class="container">
              <h2>Matthew Pisano</h2>
              <p class="title">Group Member</p>
              <p>Graduate CS student @ RPI</p>
              <p>BIO HERE</p>
              <p>
                <button class="button">
                  <a href="mailto:pisanm2@rpi.edu">Contact</a>
                </button>
              </p>
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
