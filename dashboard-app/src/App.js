import React from 'react';
import { Tv } from './components/Tv.js'
import { Movie } from './components/Movie.js'
import Navbar from 'react-bootstrap/Navbar';
import ButtonToolbar from 'react-bootstrap/ButtonToolbar'
import Button from 'react-bootstrap/Button'
import ButtonGroup from 'react-bootstrap/ButtonGroup'
import Container from 'react-bootstrap/Container'
import Col from 'react-bootstrap/Col'
import Row from 'react-bootstrap/Row'
import './App.css';

const buttonWidth = {
  width: '125px'
};

const dotenv = require('dotenv');
  
dotenv.config();

// main class definiton
export class App extends React.Component {

  // constructor - allow the use of props and state
  constructor(props) {
    super(props);
    // setup clicks for state changes
    this.handleTvClick = this.handleTvClick.bind(this);
    this.handleMovieClick = this.handleMovieClick.bind(this);

    // create state object
    this.state = {
      content: <Tv/>
    };
  }

  // for tv click
  handleTvClick() {
    this.setState({content: <Tv />});
  }

  // for movie click
  handleMovieClick() {
    this.setState({content: <Movie />});
  }

  // render function
  render() {
    return (
      <div>
        <Navbar bg="dark" variant="dark">
          <Navbar.Brand>Korber Home</Navbar.Brand>
        </Navbar>
        <div>
          <br/>
          <h3 align="center">
            Downloader
          </h3>
          <br/>
          <Container>
            <Row>
              <Col/>
              <Col>
                <ButtonToolbar>
                  <ButtonGroup>
                    <Button onClick={this.handleTvClick} variant="outline-secondary" style={buttonWidth}>TV Shows</Button>
                    <Button onClick={this.handleMovieClick}  variant="outline-secondary" style={buttonWidth}>Movies</Button>
                  </ButtonGroup>
                </ButtonToolbar>
              </Col>
              <Col/>
            </Row>
          </Container>
          <br/>
          {this.state.content}
        </div>
        <div>
          <footer className="page-footer">
            <div className="footer-copyright">
              <div className="container" align="center">
                © 2020 Korber Web Based Solutions
              </div>
            </div>
          </footer>
        </div>
      </div>
    );
  }
}