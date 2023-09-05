import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [message, setMessage] = useState('');



  return (
    <div className="App">
      {/* Bootstrap Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
        <a className="navbar-brand" href="/">React Frontend</a>
        <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav">
            <li className="nav-item active">
              <a className="nav-link" href="/">Home <span className="sr-only">(current)</span></a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="#">Another Page</a>
            </li>
          </ul>
        </div>
      </nav>

      {/* Sidebar and Main Content */}
      <div className="container-fluid">
        <div className="row">
          {/* Sidebar */}
          <nav className="col-md-3 col-lg-2 d-md-block bg-light sidebar">
            <div className="position-sticky">
              <ul className="nav flex-column">
                <li className="nav-item">
                  <a className="nav-link active" href="/">
                    Dashboard
                  </a>
                </li>
                <li className="nav-item">
                  <a className="nav-link" href="#">
                    Another Link
                  </a>
                </li>
                {/* Add more sidebar links as required */}
              </ul>
            </div>
          </nav>

          {/* Main content */}
          <main className="col-md-9 ml-sm-auto col-lg-10 px-md-4">
            <h2>Dashboard</h2>
            <p>{message}</p>
            <iframe src="http://127.0.0.1:5000/dash/" title="Dash App" width="100%" height="600"></iframe>
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
