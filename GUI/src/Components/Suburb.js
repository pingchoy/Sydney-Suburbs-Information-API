import React, { Component } from 'react';
import { Tabs, Tab } from 'react-materialize';
import NavBar from './Navbar'
import { Link, Redirect } from 'react-router-dom'
import FooterBar from "./FooterBar";
class Suburb extends Component {
    state = {
        suburb_name: '',
        post_code: '',
        nearby_data: '',
        suburb_data: '',
        school_data: '',
        train_data: '',
        weather_data: '',
        map_showing: false,
        train_map: '',
        restaurant_data: '',
        fuel_data: '',
        E10_display: false,
        P98_display: false,
        P95_display: false,
        U91_display: false,
        property_data: '',
        predict_school_data: [],

    }

    componentWillReceiveProps(nextProps) {

        window.location.reload()
    }
    componentDidMount() {
        document.title = this.props.location.state.suburb_name + ' · Sydney Analytics'
        if (this.props.location.state) {
            this.fetchData()
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
            })
            .catch(console.log)
    }

    fetchData = () => {
        this.setState({
            suburb_name: this.props.location.state.suburb_name,
            post_code: this.props.location.state.post_code,
        }, function () {
            let queryString = "/suburbs/search?query=" + this.state.suburb_name

            fetch(queryString)
                .then(res => res.json())
                .then((data) => {
                    this.setState({ suburb_data: data.results[0] })
                })
                .then(() => {
                    queryString = "/train-stations/nearest?latitude=" + this.state.suburb_data.latitude + "&longitude=" + this.state.suburb_data.longitude
                    fetch(queryString)
                        .then(res => res.json())
                        .then((data) => {

                            this.setState({ train_data: data })
                            queryString = "/suburbs/" + this.state.suburb_data.id + "/nearest"
                            fetch(queryString)
                                .then(res => res.json())
                                .then((data) => {
                                    this.setState({ nearby_data: data })
                                })
                                .catch(console.log)

                        })
                        .catch(console.log)

                    queryString = "/weather/?suburb_id=" + this.state.suburb_data.id
                    fetch(queryString)
                        .then(res => {
                            if (!res.ok) throw new Error(res.status)
                            else
                                return res.json()
                        })
                        .then((data) => {
                            this.setState({ weather_data: data.results[0] })

                        })
                        .catch((error) => {
                            console.log(error)
                        })

                    queryString = "/suburbs/" + this.state.suburb_data.id + "/schools"
                    // console.log(queryString)
                    fetch(queryString)
                        .then(res => res.json())
                        .then((data) => {
                            this.setState({ school_data: data })
                            for (let i in this.state.school_data) {
                                queryString = "/schools/" + this.state.school_data[i].id + "/predict"
                                fetch(queryString)
                                    .then(res => res.json())
                                    .then((data) => {
                                        var schoolData = { data: this.state.school_data[i], predict: data }
                                        var stateData = (this.state.predict_school_data).concat(schoolData)
                                        this.setState({ predict_school_data: stateData })
                                    })
                                    .catch((error) => {

                                    })
                            }

                        })
                        .catch((error) => {

                        })


                    queryString = "/suburbs/" + this.state.suburb_data.id + "/restaurants"
                    fetch(queryString)
                        .then(res => {
                            if (!res.ok) throw new Error(res.status)
                            else
                                return res.json()
                        })
                        .then((data) => {

                            this.setState({ restaurant_data: data.results })


                        })
                        .catch((error) => {
                            console.log(error)
                        })

                    queryString = "/suburbs/" + this.state.suburb_data.id + "/fuel-prices"
                    fetch(queryString)
                        .then(res => {
                            if (!res.ok) throw new Error(res.status)
                            else
                                return res.json()
                        })
                        .then((data) => {

                            this.setState({ fuel_data: data })



                        })
                        .catch((error) => {
                            console.log(error)
                        })

                    queryString = "/suburbs/" + this.state.suburb_data.id + "/property"
                    fetch(queryString)
                        .then(res => {
                            if (!res.ok) throw new Error(res.status)
                            else
                                return res.json()
                        })
                        .then((data) => {
                            // console.log(data)
                            this.setState({ property_data: data })
                            console.log(this.state)

                        })
                        .catch((error) => {
                            console.log(error)
                        })
                })
                .catch(console.log)
        })


    }

    mapWeather = () => {
        let tableElements = []
        let arr = []
        // get all dates
        for (let item in this.state.weather_data) {
            let date = item.match(/[0-9]?[0-9][A-Z][a-z][a-z]/)
            if (date != null) {
                // console.log(date[0])
                if (!arr.includes(date[0])) {
                    arr.push(date[0])
                }
            }
        }
        // console.log(arr)
        for (let i in arr) {
            let str = 'condition_' + arr[i]
            // console.log(str)
            let forecast = this.state.weather_data[str]
            // console.log(forecast)
            str = "forecast_" + arr[i]
            let condition = this.state.weather_data[str]
            // console.log(condition)

            tableElements.push(<tr key={i}><td className="center">{arr[i]}</td><td className="center">{forecast}</td><td className="center">{condition}&deg;C</td></tr>)

        }

        return tableElements
    }
    Loading = () => {
        if (this.state.train_data == null) {
            return <tr> <th>Loading...</th><th>Loading...</th><th>Loading...</th></tr>
        }
    }

    loadTrainMap = () => {
        let queryString = '/suburbs/' + this.state.suburb_data.id + '/train-stations'
        fetch(queryString, {
            headers: {
                'Content-Type': 'image/png'
            },
        })
            .then(res => {
                if (!res.ok) throw new Error(res.status)
                else
                    return res
            })
            .then((data) => {
                // console.log(data)
                this.setState({ train_map: <img id='train-map' alt='' src={'/suburbs/' + this.state.suburb_data.id + '/train-stations'}></img> })
                // this.setState({ train_map: data.results[0] })
                // console.log(this.state)

            })
            .catch((error) => {
                this.setState({ train_map: <h3>No map available for this suburb</h3> })
            })

    }

    onExpand = (e) => {
        console.log(e.target.value)
        let stateName = e.target.value + "_display"
        this.setState({ [stateName]: !this.state[stateName] })
        console.log(this.state.E10_display)
    }
    render() {
        if (!this.props.location.state) {
            return <Redirect to='/' />
        }
        return (
            <div>
                <NavBar />
                <nav className="z-depth-0">
                    <div className="nav-wrapper blue-grey">
                        <div className="container">
                            <div className="row">
                                <div className="col s8">
                                    <a href="/" className="breadcrumb">Suburbs</a>
                                    <span className="breadcrumb">{this.state.suburb_name}</span>
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
                    <div className="row pt-15">
                        <div className="col s5">
                            <div className="card sa-card z-depth-0">
                                <div className="card-image">
                                    <iframe title="maps"
                                            height="250"
                                            frameBorder="0"
                                            src={"https://www.google.com/maps/embed/v1/place?key=AIzaSyDD11KpJgAKV_NcnJ3buc7ehLwSQi41CCk&q=" + this.state.suburb_name + ",NSW,AU"}>
                                    </iframe>
                                </div>
                                <div className="card-content">
                                    <span className="card-heading">{this.state.suburb_name}</span>
                                    {this.state.suburb_data.locality ? <span className="card-subtitle grey-text text-darken-2">{this.state.suburb_data.locality}</span> : '' }
                                </div>
                                <div className="card-action">
                                    <strong>Postcode</strong> <span class="right card-value">{this.state.post_code}</span>
                                </div>
                                <div className="card-action">
                                    <strong>Area</strong> <span class="right card-value">{parseFloat(this.state.suburb_data.sqkm).toFixed(2)} km<sup>2</sup></span>
                                </div>
                            </div>
                            <div className="card sa-card sa-card-primary z-depth-0">
                                <div className="card-content">
                                    <span className="card-heading">Current Weather</span>
                                    <div className="row row-clear">
                                        <div className="col s4 center">
                                            <strong>Temp</strong><br />
                                            <span className="card-value">{this.state.weather_data.temp}&deg;C</span>
                                        </div>
                                        <div className="col s4 center">
                                            <strong>Humidity</strong><br />
                                            <span className="card-value">{this.state.weather_data.humidity}%</span>
                                        </div>
                                        <div className="col s4 center">
                                            <strong>Pressure</strong><br />
                                            <span className="card-value">{this.state.weather_data.pressure} Pa</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="card-action">
                                    <span className="card-heading">Weather Forecast</span>

                                    <table className="table-compact striped">
                                        <thead>
                                        <tr>
                                            <th className="center">Date</th>
                                            <th className="center">Condition</th>
                                            <th className="center">Temp</th>
                                        </tr>
                                        </thead><tbody>
                                    {this.mapWeather()}
                                    </tbody>
                                    </table>

                                </div>
                            </div>
                        </div>
                        <div className="col s7">
                            <div className="card sa-card sa-card-primary z-depth-0">
                                <div className="card-content">
                                    <span className="card-heading">Nearby Suburbs</span>
                                    <div className="sa-comma-list">
                                        {this.state.nearby_data && this.state.nearby_data.map(nearby => {
                                            return <span key={nearby.name}><Link className='nearby' to={{ pathname: '/suburb/' + nearby.name.replace(/\s+/g, '-').toLowerCase(), state: { suburb_name: nearby.name, post_code: nearby.post_code } }}>{nearby.name}</Link></span>
                                        })}
                                    </div>
                                </div>
                            </div>
                            <div className="card sa-card sa-card-primary z-depth-0">
                                <div className="card-content">
                                    <span className="card-heading">Demographics</span>
                                    <div className="row row-clear center">
                                        <div className="col s4">
                                            <span className="sa-demo-val">{this.state.suburb_data.population_female}</span>
                                            <span className="sa-demo-label">Female</span>
                                        </div>
                                        <div className="col s4">
                                            <span className="sa-demo-val">{this.state.suburb_data.population_male}</span>
                                            <span className="sa-demo-label">Male</span>
                                        </div>
                                        <div className="col s4">
                                            <span className="sa-demo-val">${parseFloat(this.state.suburb_data.avg_income / 1000).toFixed(0)}K</span>
                                            <span className="sa-demo-label">Avg income</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="card sa-card sa-card-primary z-depth-0">
                                <div className="card-content">
                                    <span className="card-heading">Property Statistics</span>

                                    <table className="table-compact striped">
                                        <tbody>
                                        {this.state.property_data ? Object.keys(this.state.property_data).map(key => {
                                            if (key !== 'suburb_id' && key !== 'suburb' && this.state.property_data[key] != null) {
                                                return <tr key={key}>
                                                    <td>{key.replace(/_/g, ' ').toLowerCase().split(' ').map(function(word) {
                                                        return word.replace(word[0], word[0].toUpperCase());
                                                    }).join(' ')}</td>
                                                    <td>${(this.state.property_data[key]).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}</td>
                                                </tr>
                                            } else { return <span></span> }
                                        }) : <tr><td>Loading...</td></tr>}
                                        </tbody>
                                    </table>

                                </div>
                            </div>
                            <div className="card sa-card sa-card-primary z-depth-0">
                                <div className="card-content">
                                    <span className="card-heading">Distance from Train Stations</span>
                                    <Tabs className="z-depth-0 sa-tab">
                                        <Tab title="List" active>
                                            <table className="table-compact striped">
                                                <thead>
                                                <tr>
                                                    <th>Name</th>
                                                    <th className="center">Distance</th>
                                                    <th className="center">AM Peak</th>
                                                    <th className="center">PM Peak</th>
                                                </tr>
                                                </thead>
                                                <tbody>{this.state.train_data ? this.state.train_data.map(train => {
                                                    return <tr key={train.id}><td>{train.name}</td>
                                                        <td className="center">{train.distance.toFixed(2)} km</td><td className="center">{train.morning_peak}</td>
                                                        <td className="center">{train.afternoon_peak}</td></tr>
                                                }) : <tr><th>Loading</th></tr>}</tbody>
                                            </table></Tab>
                                        <Tab title="Map">
                                            {this.state.suburb_data.id ? <img id='crime-graph' src={'/suburbs/' + this.state.suburb_data.id + '/train-stations'} alt="train stations"></img > : <div> </div>}</Tab>
                                    </Tabs>
                                </div>
                            </div>
                            <div className="card sa-card sa-card-primary z-depth-0">
                                <div className="card-content">
                                    <span className="card-heading">Schools</span>
                                    {(this.state.school_data.length === 0) ? <span>There are no schools listed in this suburb</span> :
                                        <table className="striped table-compact">
                                            <thead>
                                            <tr>
                                                <th>Name</th>
                                                <th className="center">Type</th>
                                                <th className="center">Predicted Size</th>
                                            </tr>
                                            </thead>
                                            <tbody>{this.state.predict_school_data ? Object.keys(this.state.predict_school_data).map(key => {
                                                return <tr key={key}>
                                                    <td>{this.state.predict_school_data[key].data.name}</td>
                                                    <td className="center">{this.state.predict_school_data[key].data.type}</td>
                                                    <td className="center">{this.state.predict_school_data[key].predict.size === "N/A" ? "N/A"
                                                        : parseFloat(this.state.predict_school_data[key].predict.size).toFixed(0)}</td></tr>

                                            }) : <tr><td>Loading</td></tr>}</tbody>
                                        </table>
                                    }
                                </div>
                            </div>
                            <div className="card sa-card sa-card-primary z-depth-0">
                                <div className="card-content">
                                    <span className="card-heading">Crime Rate</span>
                                    {this.state.suburb_data.id ? <img id='crime-graph' src={'/suburbs/' + this.state.suburb_data.id + '/crime-rates?start_year=2008'} alt="crime graph"></img > : <div> </div>}
                                </div>
                            </div>
                            <div className="card sa-card sa-card-primary z-depth-0">
                                <div className="card-content">
                                    <span className="card-heading">Top Restaurants</span>
                                    {this.state.restaurant_data.length === 0 ? <span>There are no restaurants in this suburb.</span> :

                                        <table className="table-compact striped">
                                            <thead>
                                            <tr>
                                                <th>Name</th>
                                                <th className="center">Rating</th>
                                                <th className="center">Avg Cost</th>
                                            </tr>
                                            </thead>
                                            <tbody>{this.state.restaurant_data ? this.state.restaurant_data.map(restaurant => {
                                                return <tr key={restaurant.id}>
                                                    <td>{restaurant.name}</td>
                                                    <td className="center">{restaurant.rating}/5 </td>
                                                    <td className="center">${restaurant.cost}</td></tr>
                                            }) : <tr><td>Loading</td></tr>}
                                            </tbody>
                                        </table>}
                                </div>
                            </div>
                            <div className="card sa-card sa-card-primary z-depth-0">
                                <div className="card-content">
                                    <span className="card-heading">Fuel Prices</span>
                                    <Tabs className="z-depth-0 sa-tab">
                                        <Tab title="E10" active>
                                            {this.state.E10_display ?
                                                <div>
                                                    <table class="table-compact striped">
                                                        <thead>
                                                        <tr>
                                                            <th>Date</th>
                                                            <th>Price</th>

                                                        </tr>
                                                        </thead>
                                                        <tbody>{this.state.fuel_data ? Object.keys(this.state.fuel_data['E10']).map(key => {
                                                            return <tr>
                                                                <td>{key.replace(/_/g, ' ')}</td>
                                                                {this.state.fuel_data['E10'][key] === 0 ? <td>N/A</td> :
                                                                    <td>{parseFloat(this.state.fuel_data['E10'][key]).toFixed(2)} Cents per litre</td>}
                                                            </tr>
                                                        }) : <tr><td>Loading...</td></tr>}
                                                        </tbody>
                                                    </table>
                                                    <button className='btn blue darken-1 expandBtn' value='E10' onClick={this.onExpand} > See Less </button>
                                                </div> : <button className='btn blue darken-1 expandBtn' value='E10' onClick={this.onExpand} > Expand </button>
                                            }
                                        </Tab>
                                        <Tab title="P98">
                                            {this.state.P98_display ?
                                                <div>
                                                    <table className="table-compact striped">
                                                        <thead>
                                                        <tr>
                                                            <th>Date</th>
                                                            <th>Price</th>

                                                        </tr>
                                                        </thead>
                                                        <tbody>{this.state.fuel_data ? Object.keys(this.state.fuel_data['P98']).map(key => {
                                                            return <tr>
                                                                <td>{key.replace(/_/g, ' ')}</td>
                                                                {this.state.fuel_data['P98'][key] === 0 ? <td>N/A</td> :
                                                                    <td>{parseFloat(this.state.fuel_data['P98'][key]).toFixed(2)} Cents per litre</td>}
                                                            </tr>
                                                        }) : <tr><td>Loading...</td></tr>}
                                                        </tbody>
                                                    </table>
                                                    <button className='btn blue darken-1 expandBtn' value='P98' onClick={this.onExpand} > See Less </button>
                                                </div>
                                                : <button className='btn blue darken-1 expandBtn' value='P98' onClick={this.onExpand} > Expand </button>
                                            }
                                        </Tab>
                                        <Tab title="P95">
                                            {this.state.P95_display ?
                                                <div>
                                                    <table className="table-compact striped">
                                                        <thead>
                                                        <tr>
                                                            <th>Date</th>
                                                            <th>Price</th>

                                                        </tr>
                                                        </thead>
                                                        <tbody>{this.state.fuel_data ? Object.keys(this.state.fuel_data['P95']).map(key => {
                                                            return <tr>
                                                                <td>{key.replace(/_/g, ' ')}</td>
                                                                {this.state.fuel_data['P95'][key] === 0 ? <td>N/A</td> :
                                                                    <td>{parseFloat(this.state.fuel_data['P95'][key]).toFixed(2)} Cents per litre</td>}
                                                            </tr>
                                                        }) : <tr><td>Loading...</td></tr>}
                                                        </tbody>
                                                    </table>
                                                    <button className='btn blue darken-1 expandBtn' value='P95' onClick={this.onExpand} > See Less </button>
                                                </div> : <button className='btn blue darken-1 expandBtn' value='P95' onClick={this.onExpand} > Expand </button>
                                            }
                                        </Tab>
                                        <Tab title="U91">
                                            {this.state.U91_display ?
                                                <div>
                                                    <table className="table-compact striped">
                                                        <thead>
                                                        <tr>
                                                            <th>Date</th>
                                                            <th>Price</th>

                                                        </tr>
                                                        </thead>
                                                        <tbody>{this.state.fuel_data ? Object.keys(this.state.fuel_data['U91']).map(key => {
                                                            return <tr>
                                                                <td>{key.replace(/_/g, ' ')}</td>
                                                                {this.state.fuel_data['U91'][key] === 0 ? <td>N/A</td> :
                                                                    <td>{parseFloat(this.state.fuel_data['U91'][key]).toFixed(2)} Cents per litre</td>}
                                                            </tr>
                                                        }) : <tr><td>Loading...</td></tr>}
                                                        </tbody>
                                                    </table>
                                                    <button className='btn blue darken-1 expandBtn' value='U91' onClick={this.onExpand} > See Less </button>
                                                </div>
                                                : <button className='btn blue darken-1 expandBtn' value='U91' onClick={this.onExpand} > Expand </button>
                                            }
                                        </Tab>
                                    </Tabs>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
                <FooterBar />
            </div >);
    }
}

export default Suburb;