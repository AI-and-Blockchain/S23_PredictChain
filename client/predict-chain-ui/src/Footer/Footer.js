import './Footer.css'

function Footer() {
    return (
        <div className="fixed-footer">
          <nav>
            <a href="javascript:void(0)" style={{fontSize: 'xx-large', fontWeight: '900', color: '#ffffff', marginRight: '80px', marginLeft: '100px'}}>PredictChain</a>
            <a href="javascript:void(0)" style={{marginLeft: '300px'}}>Create Account</a>
            <a href="javascript:void(0)" style={{marginLeft: '100px'}}>Login</a>
            <a href="javascript:void(0)"style={{marginLeft: '100px'}}>FAQ</a>
            <a href="javascript:void(0)" style={{marginLeft: '100px'}}>Meet The Team</a>
            <a href="https://github.com/AI-and-Blockchain/S23_PredictChain" style={{marginLeft: '100px'}}>Docs</a>
            <a href="#" style={{marginLeft: '100px'}}>Back to top</a>
          </nav>       
        </div>
    );
}

export default Footer;