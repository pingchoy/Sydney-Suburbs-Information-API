import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import logo from '../img/logo.svg'
class NavBar extends Component {

    render() {
        return (
            <nav class="z-depth-0">
                <div className="nav-wrapper blue-grey darken-4">
                    <div className="container">
                    <a className="brand-logo" href="/"><img className="left" src={logo} alt="Sydney Analytics" height="44" /> Sydney Analytics</a>
                    <ul id="nav-mobile" className="right">
                        {this.props.loggedIn ? <li className='links'><Link to='/'>Logout</Link></li> : <li className='links'><Link to='/login'>Admin</Link></li>}
                    </ul>
                </div>
                </div>
            </nav>
        );
    }
}

export default NavBar;