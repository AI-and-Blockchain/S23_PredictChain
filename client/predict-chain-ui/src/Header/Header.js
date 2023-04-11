import './Header.css';

function Header() {
  return (
    <div className="fixed-header" id="#">
      <div className="container">
          <nav>
            <a href="/" style={{fontSize: 'xx-large', fontWeight: '900', color: '#ffffff', marginRight: '50px', marginLeft: '100px'}}>PredictChain</a>
            <a href="/register" style={{fontSize: 'x-large',marginLeft: '350px'}}>Create Account</a>
            <a href="/login" style={{fontSize: 'x-large',marginLeft: '150px'}}>Login</a>
            <a href="/faq" style={{fontSize: 'x-large',marginLeft: '150px'}}>FAQ</a>
            <a href="/mtt" style={{fontSize: 'x-large',marginLeft: '150px'}}>Meet The Team</a>
            <a href="http://localhost:8031/docs" target="_blank" style={{fontSize: 'x-large', marginLeft: '150px'}}>Docs</a>
          </nav>
      </div>
    </div>
  );
}

export default Header;