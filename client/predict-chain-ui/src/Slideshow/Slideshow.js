
function Slideshow() {
  return (
    <div>
        <h1 style={{textAlign: "center",  textDecoration: "underline"}}>Example Models We Provide</h1>
        <div className="image-gallery-container" style={{width: "75%", marginLeft: "12.5%"}}>
            <img src={require('../img/perceptrons.png')} className="slideshow-image" alt="Perceptrons"/>
            <img src={require('../img/mpl.png')} className="slideshow-image" alt="Multi-Layered Perceptrons"/>
        </div>
        <div className="image-gallery-container" style={{width: "75%", marginLeft: "12.5%"}}>
            <h2 style={{marginTop: "-80px", marginLeft: "175px"}}>Perceptrons</h2>
            <h2 style={{marginTop: "0px", marginRight: "65px"}}>Multi-Layered Perceptrons</h2>
        </div>

        <div className="image-gallery-container">
            <img style={{marginLeft: "40px"}}src={require('../img/rnn.png')} className="slideshow-image" alt="Recurrent Neural Networks"/>
            <img src={require('../img/lstm.png')} className="slideshow-image" alt="Long Short-Term Memory Networks"/>
            <img style={{marginRight: "40px"}} src={require('../img/gru.png')} className="slideshow-image" alt="Gated Recurrent Unit Networks"/>
        </div>
        <div className="image-gallery-container">
            <h2 style={{marginTop: "-240px", marginLeft: "125px"}}>Recurrent Neural Networks</h2>
            <h2 style={{marginTop: "-5px", marginRight: "-40px"}}>Long Short-Term Memory Networks</h2>
            <h2 style={{marginTop: "-140px", marginRight: "100px"}}>Gated Recurrent Unit Networks</h2>
        </div>

    </div>
  );
}

export default Slideshow;