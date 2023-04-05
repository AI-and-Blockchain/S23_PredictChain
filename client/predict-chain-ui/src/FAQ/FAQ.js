import Header from '../Header/Header';
import Footer from '../Footer/Footer';
import "./FAQ.css"
function FAQ() {
    return (
        <div>
            <Header/>
            <h1 style={{textAlign: "center", fontSize: "56px", textDecoration: "underline"}}>Frequently Asked Questions</h1>
            <br/>
            <div className="containertext">
                <div className="text" style={{marginTop: '20px', marginLeft: '100px', marginRight: '100px', textAlign: "center"}}>
                    <h1>How is the cost to train a model calculated?</h1>
                    <h4 style={{fontSize: "30px", fontWeight: "lighter"}}>Templated Answer</h4>
                </div>
            </div>
            <div className="containertext">
                <div className="text" style={{marginTop: '20px', marginLeft: '100px', marginRight: '100px', textAlign: "center"}}>
                    <h1>How am I rewarded for uploading data?</h1>
                    <h4 style={{fontSize: "30px", fontWeight: "lighter"}}>Templated Answer</h4>
                </div>
            </div>
            <div className="containertext">
                <div className="text" style={{marginTop: '20px', marginLeft: '100px', marginRight: '100px', textAlign: "center"}}>
                    <h1>How is my information kept secure?</h1>
                    <h4 style={{fontSize: "30px", fontWeight: "lighter"}}>Templated Answer</h4>
                </div>
            </div>
            <div className="containertext">
                <div className="text" style={{marginTop: '20px', marginLeft: '100px', marginRight: '100px', textAlign: "center"}}>
                    <h1>What is PredictChain?</h1>
                    <h4 style={{fontSize: "30px", fontWeight: "lighter"}}>Templated Answer</h4>
                </div>
            </div>
            <div className="containertext">
                <div className="text" style={{marginTop: '20px', marginLeft: '100px', marginRight: '100px', textAlign: "center"}}>
                    <h1>What is PredictChain?</h1>
                    <h4 style={{fontSize: "30px", fontWeight: "lighter"}}>Templated Answer</h4>
                </div>
            </div>
            <div className="containertext">
                <div className="text" style={{marginTop: '20px', marginLeft: '100px', marginRight: '100px', textAlign: "center"}}>
                    <h1>What is PredictChain?</h1>
                    <h4 style={{fontSize: "30px", fontWeight: "lighter"}}>Templated Answer</h4>
                </div>
            </div>
            <br/>
            <Footer/>
        </div>
    );
  }
export default FAQ;