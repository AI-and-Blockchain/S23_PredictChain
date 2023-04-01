import React, {useState, useEffect} from 'react';
import './HomePage.css'
import Header from '../Header/Header';
import Footer from '../Footer/Footer';

function HomePage() {
  return (
    <div>
        <Header/>
        <div className="containertext">
          <div className="img" style={{marginLeft: '200px', marginTop: '50px'}}>
            <img src={require('../img/prediction.png')} style={{width: '400px', height: '400px'}}/>
          </div>
          <div className="text" style={{marginLeft: '100px', marginRight: '200px', marginTop: '50px'}}>
            <h1>What is PredictChain?</h1>
            <h4>PredictChain is a marketplace for predictive AI models. Users will be able to upload datasets to train predictive models, or submit queries to those models. These various models will be operated by a central node or nodes with computing resources available. A variety of models will be made available, ranging from cheap, fast, and simple to more expensive, slower, and more powerful. This will allow for a large variety of predictive abilities for both simple and complex patterns. All the past predictions form these models will be stored on the blockchain for public viewing.</h4>
          </div>
        </div>
        <div className="containertext">
          <div className="text" style={{marginLeft: '200px', marginRight: '100px', marginTop: '50px'}}>
            <h1>How do we differ from our competitors?</h1>
            <h4>Our motivation is to fill a similar niche to marketplace DApps, but will accommodate to the user more. We are working towards a more varied experience when it comes to decentralized ML platforms.  Over the course of the month, we plan to improve upon this idea to provide users with more flexibility in their use cases.</h4>
          </div>
          <div className="img" style={{marginRight: '200px', marginTop: '50px'}}>
            <img src={require('../img/differentiate.jpg')}  style={{width: '600px', height: '400px', borderRadius: '80px'}}/>
          </div>
        </div>
        <Footer/>
    </div>
  );
}

export default HomePage;
