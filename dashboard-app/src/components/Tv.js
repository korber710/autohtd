// library imports
import React from 'react'
import InputGroup from 'react-bootstrap/InputGroup'
import FormControl from 'react-bootstrap/FormControl'
import Button from 'react-bootstrap/Button'
import axios from 'axios'
import Container from 'react-bootstrap/Container'
import Col from 'react-bootstrap/Col'
import Row from 'react-bootstrap/Row'
import Table from 'react-bootstrap/Table'
import {toast, ToastContainer} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Spinner from 'react-bootstrap/Spinner'

// class definition
export class Tv extends React.Component {
    // constructor - allow the use of props and state
    constructor(props) {
        super(props)
        // setup clicks for state changes
        this.handleSearchClick = this.handleSearchClick.bind(this)
        this.handleSearchChange = this.handleSearchChange.bind(this)
        this.handleAddClick = this.handleAddClick.bind(this)
        this.handleSeasonChange = this.handleSeasonChange.bind(this)
        // // create state object
        this.state = {
            returnDesc: "",
            searchShow: "",
            foundShow: "",
            foundSeasons: 0,
            showDiv: <div/>,
            seasonChoice: ""
        }
    }
    // for add click
    handleAddClick() {
        this.setState({
            showDiv: 
                <div style={{textAlign: 'center'}}>
                    <br/>
                    <br/>
                    <Spinner style={{display: 'inline-block'}} animation="grow" variant="dark" />
                </div>
        })
        const data = {
            name: this.state.foundShow,
            season: parseInt(this.state.seasonChoice, 10),
            current: []
        }
        axios.post(`http://${process.env.REACT_APP_HOST_IP}:5000/api/v1/tv/add`, data)
        .then(res => {
            console.log(res.data)
            toast.success(
                'Added show', 
                {containerId: 'A'}
            )
            this.setState({
                showDiv: 
                    <div/>
            })
        })
    }
    // for search click
    handleSearchClick() {
        this.setState({
            showDiv: 
                <div style={{textAlign: 'center'}}>
                    <br/>
                    <br/>
                    <Spinner style={{display: 'inline-block'}} animation="grow" variant="dark" />
                </div>
        })
        axios.post(`http://${process.env.REACT_APP_HOST_IP}:5000/api/v1/tv/search`, {name: this.state.searchShow})
        .then(res => {
            console.log(res.data)
            this.setState({returnDesc: res.data.description})
            this.setState({foundShow: res.data.data.name})
            this.setState({foundSeasons: res.data.data.seasons})
            this.setState({
                showDiv: 
                    <div>
                        <Container>
                            <Row>
                                <Col style={{textAlign: 'center'}}>
                                    <Table bordered size="sm">
                                        <thead>
                                            <tr>
                                                <td>Name</td>
                                                <td>Seasons</td>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>{this.state.foundShow}</td>
                                                <td>{this.state.foundSeasons}</td>
                                            </tr>
                                        </tbody>
                                    </Table>
                                </Col>
                            </Row>
                            <Row>
                                <Col>
                                    <FormControl onChange={this.handleSeasonChange} placeholder="season"></FormControl>
                                </Col>
                                <Col>
                                    <Button style={{width: '100%'}} onClick={this.handleAddClick} variant="success">Add</Button>
                                </Col>
                            </Row>
                        </Container>
                    </div>
            })
        })
    }
    // for search change
    handleSearchChange(e) {
        this.setState({searchShow: e.target.value})
    }
    // for add season change
    handleSeasonChange(e) {
        this.setState({seasonChoice: e.target.value})
    }
    // render method
    render() {
        return (
            <div className="mid-page">
                <h5 align="center">
                    TV Shows
                </h5>
                <ToastContainer enableMultiContainer containerId={'A'} position={toast.POSITION.TOP_CENTER} />
                <InputGroup className="mb-3">
                    <FormControl onChange={this.handleSearchChange} placeholder="Show name"/>
                    <InputGroup.Append>
                        <Button onClick={this.handleSearchClick} variant="outline-secondary">Search</Button>
                    </InputGroup.Append>
                </InputGroup>
                {this.state.showDiv}
            </div>
        );
    }
}
