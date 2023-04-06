
function Slideshow() {
  return (
    <div>
        <div className="image-gallery-container">
            <h1 style={{textAlign: "center",  textDecoration: "underline"}}>Example Models We Provide</h1>
            <img src={require('../img/decision-tree.png')} style={{marginLeft: "50px", border: "4px solid black", borderRadius: "3px"}} alt="Decision Trees"/>
            <img src={require('../img/perceptrons.png')} style={{marginLeft: "25px", marginRight: "25px", border: "4px solid black", borderRadius: "3px"}} alt="Perceptrons"/>
            <img src={require('../img/nn.png')} style={{width: "600px", border: "4px solid black", borderRadius: "3px"}} alt="Neural Networks"/>
        </div>
        <h2 style={{display: "inline", marginLeft: "250px"}}>Decision Trees</h2><h2 style={{display: "inline", marginLeft: "450px"}}>Perceptrons</h2><h2 style={{display: "inline", marginLeft: "435px"}}>Neural Networks</h2>
    </div>
  );
}

export default Slideshow;