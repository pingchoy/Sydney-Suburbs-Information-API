import React, { Component } from 'react';
import NavBar from './Navbar'
import logo from '../img/logo.svg'
import FooterBar from "./FooterBar";
class Login extends Component {
    state = {
        email: '',
        password: '',
        loginToken: '',
        loginError: ''
    }
    componentDidMount() {
        document.title = 'Login · Sydney Analytics'
    }
    handleChange = (e) => {
        this.setState({
            [e.target.id]: e.target.value
        })
    }

    handleSubmit = (e) => {
        e.preventDefault()
        let queryString = "/users/token"
        fetch(queryString, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'username=' + this.state.username + '&password=' + this.state.password
        })
            .then(res => {
                if (res.status === 401) {
                    throw new Error('Login Failed')
                }
                return res.json()
            })
            .then((data) => {
                console.log(data)
                this.setState({ loginToken: data.token })
                this.props.history.push('/analytics', {
                        token: data,
                    }
                )
            })
            .catch((error) => {
                this.setState({ loginError: 'Login Failed' })

            })
    }

    render() {
        let loginError = this.state.loginError
        return (
            <div>
                <NavBar />
                <main className="container">
                    <div className="row">
                        <div className="col s12">
                            <div className="section section-homepage center">
                                <a href="/"><img src={logo} alt="Sydney Analytics" width="128" /></a>
                                <h3 className="logo-text">Admin Login</h3>
                            </div>
                        </div>
                    </div>
                    <div className="row">
                        <form onSubmit={this.handleSubmit}>
                            <div className="col s4 offset-s4">
                                <div className="input-field">
                                    <label htmlFor="username">Username</label>
                                    <input type="text" id="username" onChange={this.handleChange} />
                                </div>
                                <div className="input-field">
                                    <label htmlFor="password">Password</label>
                                    <input type="password" id="password" onChange={this.handleChange} />
                                </div>
                                <div className="input-field center">
                                    <button className="btn blue darken-1 login-button">Login</button>
                                    <div className="red-text center">
                                        <br />
                                        {loginError}
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </main>
                <FooterBar />
            </div>
        );
    }
}

export default Login;