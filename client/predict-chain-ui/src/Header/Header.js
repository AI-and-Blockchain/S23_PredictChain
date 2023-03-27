import './Header.css'

function Header() {
    return (
        <div className="fixed-header" id="#">
          <div className="container">
              <nav>
                <a href="javascript:void(0)" style={{fontSize: 'xx-large', fontWeight: '900', color: '#ffffff', marginRight: '50px', marginLeft: '100px'}}>PredictChain</a>
                <a href="/create" style={{marginLeft: '400px'}}>Create Account</a>
                <a href="javascript:void(0)" style={{marginLeft: '150px'}}>Login</a>
                <a href="javascript:void(0)"style={{marginLeft: '150px'}}>FAQ</a>
                <a href="javascript:void(0)" style={{marginLeft: '150px'}}>Meet The Team</a>
                <a href="https://github.com/AI-and-Blockchain/S23_PredictChain" style={{marginLeft: '150px'}}>Docs</a>
              </nav>
          </div>
        </div>
    );
}

export default Header;