
function Slideshow() {
  return (
    <div>
        <div className="image-gallery-container">
            <h1 style={{textAlign: "center"}}>Example Models We Provide</h1>
            <img src={require('../img/image-src.png')} style={{marginLeft: "150px"}} alt="Snow"/>
            <img src={require('../img/image-src.png')} style={{marginLeft: "200px"}} alt="Forest"/>
            <img src={require('../img/image-src.png')} style={{marginLeft: "200px"}} alt="Mountains"/>
        </div>
        <h2 style={{display: "inline", marginLeft: "150px"}}>Decision Trees</h2><h2 style={{display: "inline", marginLeft: "420px"}}>Perceptrons</h2><h2 style={{display: "inline", marginLeft: "445px"}}>Neural Networks</h2>
    </div>
  );
}

export default Slideshow;