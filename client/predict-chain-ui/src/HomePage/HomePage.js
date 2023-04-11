import React from 'react';
import Header from '../Header/Header';
import Footer from '../Footer/Footer';
import Slideshow from '../Slideshow/Slideshow';
import '../Slideshow/Slideshow.css';
import './HomePage.css';

function HomePage() {
  return (
    <div>
        <Header/>
        <div className="containertext">
          <div className="img" style={{marginLeft: '200px', marginTop: '50px'}}>
            <img src={require('../img/prediction.png')} style={{width: '400px', height: '400px'}}/>
          </div>
          <div className="text" style={{marginLeft: '100px', marginRight: '200px', marginTop: '50px'}}>
            <h1 style={{textDecoration: "underline"}}>What is PredictChain?</h1>
            <h4 style={{fontSize: "30px", fontWeight: "lighter"}}>PredictChain is a marketplace for predictive AI models. Users will be able to upload datasets to train predictive models, or submit queries to those models. These various models will be operated by a central node or nodes with computing resources available. A variety of models will be made available, ranging from cheap, fast, and simple to more expensive, slower, and more powerful. This will allow for a large variety of predictive abilities for both simple and complex patterns. All the past predictions form these models will be stored on the blockchain for public viewing.</h4>
          </div>
        </div>
        <div className="containertext">
          <div className="text" style={{marginLeft: '200px', marginRight: '100px', marginTop: '50px'}}>
            <h1 style={{textDecoration: "underline"}}>How do we differ from our competitors?</h1>
            <h4 style={{fontSize: "30px", fontWeight: "lighter"}}>Our motivation is to fill a similar niche to marketplace DApps, but we intend on accommodating to the user more. We are working towards a more varied experience when it comes to decentralized ML platforms.  We plan to improve upon this idea to provide users with more flexibility in their use cases over the course of this semester.</h4>
          </div>
          <div className="img" style={{marginRight: '200px', marginTop: '50px'}}>
            <img src={require('../img/differentiate.jpg')}  style={{width: '600px', height: '400px', borderRadius: '80px'}}/>
          </div>
        </div>
        <br/>
        <br/>
        <Slideshow/>
        <br/>
        <br/>
        <div className="text" style={{marginTop: '50px'}}>
          <h1 style={{textAlign: "center", textDecoration: "underline"}}>Who are we?</h1>
          <h4 style={{marginLeft: "255px", marginRight: "255px", fontSize: "30px", fontWeight: "lighter", textAlign: "center"}}>Just a group of <a href="https://www.rpi.edu" className="temp">RPI</a> students in an AI & Blockchain class. This is our group project for the Spring 2023 semester. More in-depth detail about us and who we are located in our <a href="/mtt" className="temp">Meet The Team</a> page!</h4>
        </div>
        <br/>
        <Footer/>
    </div>
  );
}

export default HomePage;
