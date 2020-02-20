import React, { Component } from 'react';
import NavBar from './Navbar'
import { Link } from 'react-router-dom'
import FooterBar from "./FooterBar";
class SearchResults extends Component {
    state = {
        page: 1,
        data: '',
        search_term: ''
    }

    componentDidMount() {
        document.title = 'Search · Sydney Analytics'
        if (this.props.location.state) {
            this.setState({
                data: this.props.location.state.data,
                search_term: this.props.location.state.search_term
            })
        }
    }

    handleSearchChange = (event) => {
        this.setState({ suburb: event.target.value })
    }

    handleSearchSubmit = (event) => {
        event.preventDefault()
        let queryString = "/suburbs/search?query=" + this.state.suburb
        fetch(queryString)
            .then(res => res.json())
            .then((data) => {
                this.props.history.push('/search-results', {
                    data: data,
                    search_term: this.state.suburb,
                })
                this.setState({data: data,
                    search_term: this.state.suburb
                })
            })
            .catch(console.log)
    }

    nextPage = () => {
        let newPageNum = this.state.page + 1
        // console.log(this.state)
        if (newPageNum <= this.state.data.pages) {
            this.setState({ page: newPageNum },
                function () {
                    let queryString = "/suburbs/search?query=" + this.state.search_term + "&page=" + this.state.page
                    // console.log(queryString)
                    fetch(queryString)
                        .then(res => res.json())
                        .then((data) => {
                            this.setState({ data: data })
                        })
                        .catch(console.log)
                })
        }
    }

    prevPage = () => {
        let newPageNum = this.state.page - 1
        if (newPageNum > 0) {
            this.setState({ page: newPageNum },
                function () {

                    let queryString = "/suburbs/search?query=" + this.state.search_term + "&page=" + this.state.page

                    fetch(queryString)
                        .then(res => res.json())
                        .then((data) => {

                            this.setState({ data: data })
                        })
                        .catch(console.log)
                })
        }
    }
    render() {
        return (
            <div>
                <NavBar />
                <nav className="z-depth-0">
                    <div className="nav-wrapper blue-grey">
                        <div className="container">
                            <div className="row">
                                <div className="col s8">
                                    <a href="/" className="breadcrumb">Suburbs</a>
                                    <span className="breadcrumb">Search</span>
                                </div>
                                <div className="col s4">
                                    <form onSubmit={this.handleSearchSubmit}>
                                        <div className="input-field">
                                            <input id="searchBar" name="query" onChange={this.handleSearchChange} type="search" autoComplete="off" required />
                                            <label className="label-icon" htmlFor="search"><i
                                                className="material-icons">search</i></label>
                                            <i className="material-icons">close</i>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </nav>
                <main className="container">
                    <div className="row">
                        <div className="col s8">
                            <div className="section">
                                {this.state.data.results && this.state.data.results.length === 0 ? (
                                    <span>No suburbs found matching '{this.state.search_term}'</span>
                                ) : (
                                    <div>
                                        <div className="row row-clear sa-pagination pt-15 valign-wrapper">
                                            <div className="col s4"><button onClick={this.prevPage} disabled={this.state.data.page === 1} className="btn-flat waves-effect"><i className="material-icons">chevron_left</i></button></div>
                                            <div className="col s4 center">{this.state.data.page} of {this.state.data.pages}</div>
                                            <div className="col s4 text-right"><button onClick={this.nextPage} disabled={this.state.data.page === this.state.data.pages} className="btn-flat waves-effect"><i className="material-icons">chevron_right</i></button></div>
                                        </div>
                                        <div className="collection sa-collection">
                                            {this.state.data.results && this.state.data.results.map(suburb => {
                                                return <Link key={'suburb-'+suburb.id} className="collection-item blue-text darken-1" to={{ pathname: '/suburb/' + suburb.name.replace(/\s+/g, '-').toLowerCase(), state: { suburb_name: suburb.name, post_code: suburb.post_code } }}>{suburb.name}<span className="secondary-content grey-text text-darken-2">{suburb.post_code}</span></Link>
                                            })}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </main>
                <FooterBar />
            </div>);
    }
}

export default SearchResults;