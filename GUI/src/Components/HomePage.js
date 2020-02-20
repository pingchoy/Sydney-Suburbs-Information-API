import React, { Component } from 'react';
import '../css/HomePage.css'
import logo from '../img/logo.svg'
import NavBar from './Navbar'
import FooterBar from './FooterBar'

class HomePage extends Component {
    state = {
        suburb: ''
    }

    handleSuburbChange = (event) => {
        this.setState({ suburb: event.target.value })
    }

    handleSubmit = (event) => {
        event.preventDefault()
        let queryString = "/suburbs/search?query=" + this.state.suburb
        fetch(queryString)
            .then(res => res.json())
            .then((data) => {
                this.props.history.push('/search-results', {
                    data: data,
                    search_term: this.state.suburb
                })
            })
            .catch(console.log)
    }

    render() {
        return (
            <div>
                <NavBar />
                <main className="container">
                    <div className="row">
                        <div className="col s12">
                            <div className="section section-homepage center">
                                <a href="/"><img src={logo} alt="Sydney Analytics" width="128" /></a>
                                <h3 className="logo-text">Sydney Analytics</h3>
                            </div>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col s6 offset-s3">
                            <form>
                                <div className="row">
                                    <div className="input-field col s8 offset-s1">
                                        <input id="suburbs-name" value={this.state.suburb} onChange={this.handleSuburbChange} type="text" />
                                        <label id='search-label' htmlFor="suburbs-name">Search suburbs</label>
                                    </div>
                                    <div className="input-field col s2">
                                        <button className="btn-large waves-effect waves-light left blue darken-1 z-depth-0" value="submit" onClick={this.handleSubmit} name="action">Search</button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </main>
                <FooterBar />
            </div>
        );
    }
}

export default HomePage;