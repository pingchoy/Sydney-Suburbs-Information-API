import React from 'react';
import HomePage from './Components/HomePage'
import './App.css';
import { BrowserRouter, Switch, Route } from 'react-router-dom'
import SearchResult from './Components/SearchResults'
import Login from './Components/Login'
import Suburb from './Components/Suburb'
import Analytics from './Components/Analytics'
function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Switch>
          <Route path='/analytics/' component={Analytics} />
          <Route path='/login/' component={Login} />
          <Route path='/suburb/:name' component={Suburb} />
          <Route path='/search-results' component={SearchResult} />
          <Route path="/" component={HomePage} />
        </Switch>
      </div>
    </BrowserRouter>
  );
}

export default App;
