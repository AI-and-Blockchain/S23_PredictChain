import Header from "../Header/Header";
import Footer from "../Footer/Footer";

function FAQ() {
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
        Frequently Asked Questions
      </h1>
      <br />
      <div className="containertext">
        <div
          className="text"
          style={{
            marginTop: "20px",
            marginLeft: "100px",
            marginRight: "100px",
            textAlign: "center",
          }}
        >
          <h1>What is PredictChain?</h1>
          <h4 style={{ fontSize: "30px", fontWeight: "lighter" }}>
            PredictChain is a marketplace for predictive AI models. Our goal is
            to make predictive models more accessible to more potential users.
            We do this through the ease of use and transparency of PredictChain.
            Users will be able to upload datasets, request the training of train
            predictive models, or submit queries to those models. These various
            models will be operated by a central node or nodes with computing
            resources available.
          </h4>
        </div>
      </div>
      <div className="containertext">
        <div
          className="text"
          style={{
            marginTop: "20px",
            marginLeft: "100px",
            marginRight: "100px",
            textAlign: "center",
          }}
        >
          <h1>What models are available to me?</h1>
          <h4 style={{ fontSize: "30px", fontWeight: "lighter" }}>
            A variety of models will be made available, ranging from cheap,
            fast, and simple to more expensive, slower, and more powerful. This
            will allow for a large variety of predictive abilities for both
            simple and complex patterns. Specifically, these include:
            <ul style={{ textAlign: "left", width: "40%", marginLeft: "30%" }}>
              <li>Multi-layered Perceptrons</li>
              <li>Recurrent Neural Networks</li>
              <li>Long Short-term Memory Networks</li>
              <li>Gated Recurrent Unit Networks</li>
            </ul>
          </h4>
        </div>
      </div>
      <div className="containertext">
        <div
          className="text"
          style={{
            marginTop: "20px",
            marginLeft: "100px",
            marginRight: "100px",
            textAlign: "center",
          }}
        >
          <h1>How is the cost to train a model calculated?</h1>
          <h4 style={{ fontSize: "30px", fontWeight: "lighter" }}>
            The cost of training a model is governed, primarily by a single
            equation:
            <p>
              <i>model.model_complexity * mult * dataset.size</i>
            </p>
            <ul style={{ textAlign: "left", width: "70%", marginLeft: "15%" }}>
              <li>
                <b>model complexity</b> is calculated based off of the size of
                the model selected and the type of model used.
              </li>
              <li>
                <b>mult</b> is a constant multiplier, governed by the Oracle.
                This can be changed at any time, but a log of changes is
                permanently kept on the blockchain for reference
              </li>
              <li>
                The final component is the <b>size</b> of the dataset
              </li>
            </ul>
          </h4>
        </div>
      </div>
      <div className="containertext">
        <div
          className="text"
          style={{
            marginTop: "20px",
            marginLeft: "100px",
            marginRight: "100px",
            textAlign: "center",
          }}
        >
          <h1>How am I rewarded for uploading data?</h1>
          <h4 style={{ fontSize: "30px", fontWeight: "lighter" }}>
            The reward for uploading data is two-fold! You are rewarded once a
            model is trained on your data and again when that model is queried.
            In both instances, the size of the reward is calculated using the
            size of the dataset multiplied by the accuracy of the model that was
            trained using it.
          </h4>
        </div>
      </div>
      <div className="containertext">
        <div
          className="text"
          style={{
            marginTop: "20px",
            marginLeft: "100px",
            marginRight: "100px",
            textAlign: "center",
          }}
        >
          <h1>How am I rewarded for requesting a trained model?</h1>
          <h4 style={{ fontSize: "30px", fontWeight: "lighter" }}>
            The reward for training a model is based off of its accuracy. The
            more accurate the model, the higher the reward! This reward is
            dispensed whenever a user queries the trained model for a result.
          </h4>
        </div>
      </div>
      <div className="containertext">
        <div
          className="text"
          style={{
            marginTop: "20px",
            marginLeft: "100px",
            marginRight: "100px",
            textAlign: "center",
          }}
        >
          <h1>How is my information kept secure?</h1>
          <h4 style={{ fontSize: "30px", fontWeight: "lighter" }}>
            You have the choice of weather to make your dataset publicly
            available or not. When choosing to upload to IPFS, yor data is
            publicly viewable. When choosing to keep your data with us, it is
            not publicly visible. In both of these cases, your data is not
            directly visible to others. The oracle is designed to be a black box
            where only necessary information comes out. The only knowledge that
            can be gained from your dataset is through the output of the models
            that are trained on it.
          </h4>
        </div>
      </div>
      <br />
      <Footer />
    </div>
  );
}
export default FAQ;
