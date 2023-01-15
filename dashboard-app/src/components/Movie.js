// library imports
import React from 'react'
import InputGroup from 'react-bootstrap/InputGroup'
import FormControl from 'react-bootstrap/FormControl'
import Button from 'react-bootstrap/Button'
import axios from 'axios'
import Container from 'react-bootstrap/Container'
import Col from 'react-bootstrap/Col'
import Row from 'react-bootstrap/Row'
import {toast, ToastContainer} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'
import Spinner from 'react-bootstrap/Spinner'
import Table from 'react-bootstrap/Table'
import Alert from 'react-bootstrap/Alert' 

function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

// class definition
export class Movie extends React.Component {
    // constructor - allow the use of props and state
    constructor(props) {
        super(props)
        // setup clicks for state changes
        this.handleSearchClick = this.handleSearchClick.bind(this)
        this.handleSearchChange = this.handleSearchChange.bind(this)
        this.handleAddClick = this.handleAddClick.bind(this)
        // // create state object
        this.state = {
            returnDesc: "",
            searchMovie: "",
            foundMovie: "",
            movieDiv: <div/>
        }
    }
    // for add click
    handleAddClick() {
        this.setState({
            movieDiv: 
                <div style={{textAlign: 'center'}}>
                    <br/>
                    <br/>
                    <Spinner style={{display: 'inline-block'}} animation="grow" variant="dark" />
                </div>
        })
        const data = {
            name: this.state.foundMovie
        }
        axios.post(`http://${process.env.REACT_APP_HOST_IP}:5000/api/v1/movie/add`, data)
        .then(res => {
            console.log(res.data)
            toast.success(
                'Added movie', 
                {containerId: 'A'}
            )
            this.setState({
                movieDiv: 
                    <div/>
            })
        })
    }
    // for search click
    handleSearchClick() {
        this.setState({
            movieDiv: 
                <div style={{textAlign: 'center'}}>
                    <br/>
                    <br/>
                    <Spinner style={{display: 'inline-block'}} animation="grow" variant="dark" />
                </div>
        })
        axios.post(`http://${process.env.REACT_APP_HOST_IP}:5000/api/v1/movie/search`, {name: this.state.searchMovie})
        .then(res => {
            this.setState({returnDesc: res.data.description})
            this.setState({foundMovie: res.data.data.data[0].title_long})
            console.log(res.data)
            this.setState({
                movieDiv: 
                    <div>
                        <Container>
                            <Row>
                                <Col style={{textAlign: 'center'}}>
                                    <Table bordered size="sm">
                                        <thead>
                                            <tr>
                                                <td>Name</td>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>{this.state.foundMovie}</td>
                                            </tr>
                                        </tbody>
                                    </Table>
                                </Col>
                            </Row>
                            <Row>
                                <Col>
                                    <Button style={{width: '100%'}} onClick={this.handleAddClick} variant="success">Add</Button>
                                </Col>
                            </Row>
                        </Container>
                    </div>
            })
        })
        .catch(error => {
            console.log(error)
            this.setState({
                movieDiv: 
                    <div style={{textAlign: 'center'}}>
                        <br/>
                        <br/>
                        <Alert variant="danger">
                            <p>Could Not Find Results</p>
                        </Alert>
                    </div>
            })
        })
    }
    // for search change
    handleSearchChange(e) {
        this.setState({searchMovie: e.target.value})
    }
    // render method
    render() {
        return (
            <div className="mid-page">
                <h5 align="center">
                    Movies
                </h5>
                <ToastContainer enableMultiContainer containerId={'A'} position={toast.POSITION.TOP_CENTER} />
                <InputGroup className="mb-3">
                    <FormControl onChange={this.handleSearchChange} placeholder="Movie name (year)"/>
                    <InputGroup.Append>
                        <Button onClick={this.handleSearchClick} variant="outline-secondary">Search</Button>
                    </InputGroup.Append>
                </InputGroup>
                {this.state.movieDiv}
            </div>
        );
    }
}