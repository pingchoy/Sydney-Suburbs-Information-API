import React, { Component } from 'react';
import NavBar from './Navbar'
import { Redirect } from 'react-router-dom';
import { MediaBox } from 'react-materialize';
import FooterBar from "./FooterBar";

class Analytics extends Component {
    state = {
        token: this.props.location.state,
        users: '',
        analytic_img: '',
    }
    componentDidMount() {
        document.title = 'Admin · Sydney Analytics'
        if (this.props.location.state != null) {

            this.setState({ token: this.props.location.state.token})

            let queryString = "/analytics/"
            fetch(queryString, {
                headers: {
                    'Accept': 'image/png',
                    'AUTH-TOKEN': this.state.token.token.token
                }
            })
                .then(res => {
                    if (!res.ok) throw new Error(res.status)
                    else
                        return res.blob()
                })
                .then((data) => {
                    this.setState({ analytic_img: URL.createObjectURL(data)})
                })
                .catch((error) => {
                    this.setState({ analytic_img: null })
                })


            queryString = "/users/"
            fetch(queryString, {
                headers: new Headers({
                    'AUTH-TOKEN': this.state.token.token.token
                })
            })
                .then(res => {
                    if (!res.ok) throw new Error(res.status)
                    else
                        return res.json()
                })
                .then((data) => {
                    this.setState({ users: data })
                })
                .catch((error) => {
                    console.log(error)
                })
        }

    }
    render() {
        if (!this.state.token) {
            return <Redirect to='/login' />
        }
        return (
            <div>
                <NavBar loggedIn={true}></NavBar>
                <main className="container">
                    <div className="row">
                        <div className="col s7">
                            <div className="section">
                                <div className="card sa-card sa-card-admin z-depth-0">
                                    <div className="card-content">
                                        <span className="card-heading">Recent API activity</span>
                                        <MediaBox>
                                            <img className="responsive-img" alt='analytics' src={this.state.analytic_img} />
                                        </MediaBox>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col s5">
                            <div className="section">
                                <div className="card sa-card sa-card-admin z-depth-0">
                                    <div className="card-content">
                                        <span className="card-heading">Users</span>
                                        <table className="table-compact striped">
                                            <thead>
                                            <tr>
                                                <th>Username</th>
                                                <th>Role</th>
                                            </tr>
                                            </thead>
                                            <tbody>{this.state.users && this.state.users.map(user => {
                                                return <tr key={user.username}><td>{user.username}</td><td>{user.role}</td></tr>
                                            })}</tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
                <FooterBar />
            </div>
        );
    }
}

export default Analytics;