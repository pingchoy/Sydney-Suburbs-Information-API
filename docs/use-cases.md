# Use-cases

Moving this here: https://docs.google.com/document/d/1EU-uKxiB6lfXK9Jccmk5PzyRxpvRvJl9hbtKEi_eyAw/edit?usp=sharing

---

Sydney is an expansive and diverse metropolitan area of almost 700 suburbs. People moving to Sydney may find it overwhelming when trying to find a suburb that suits their particular lifestyle or living circumstances.

Sydney Data Services is a RESTful API & GUI which provides an analytical overview of Sydney, giving the user insightful information on each suburb. It aims to provide solutions to questions regarding certain aspects of livability in a particular suburb.

Overall usage and functionality is outlined below, split into each API feature.

---

### Demographics
In retrieving a suburb, whether by its identifier or search query, a user is given a high-level overview of general statistics for a given suburb. This includes: locality, state, post code, latitude, longitude, area (sqkm), male, female & total population and (total) average income.

One may find use in viewing these data as a general indicator of living conditions, such as estimated earnings and distance to other suburbs or the CBD.

### Crime rates
- Allows the user to know if the suburb they would potentially live in is safe or not.
- Understand if some suburb needs changing for the better and hence improve relations in the community.
- Potentially see which suburbs/communities will receive grants
- Allows to see which areas the police should target and keep and eye on.

### Schools
- Allows the user to see the schools around each of the suburbs (e.g. private vs public)
- Predicting the number of students who will enrol in each school in future years - good for school staff to see.

### Train stations
Provides general information regarding Sydney train stations. This includes the location and estimated morning & afternoon peak times, which can aid in making time-based decisions during congested hours in a day.

Moreover, if a suburb is specified, a user is provided with information of the closest 5 train stations to a given suburb, calculated using the respective latitudes and longitudes. This is particularly useful when taking into consideration distance to other points of interest such as the journey to a workplace or the CBD.

### Local food and restaurants
- The user can see the kind of restauraunts avaliable by cuisine, which could be useful if they are in a particular suburb.
- The ability to look at what the others recommended around the area.

### Weather
- Looking at the current and forecasted weather for the next 3 days by suburb (in degrees celsius)

### Real estate
- Looking at property prices for September 2019 - indication of the expensiveness of housing. 

### Fuel prices
Retrieves a time-series of average monthly fuel prices (in Cents per litre) for Sydney suburbs for the past 3 years, per fuel type out of P98, P95, U91 & E10. This enables a user to select a particular fuel type to further analyze the overall expectation when re-fueling a vehicle within a given suburb.

Furthermore, the ability to forecast a monthly average fuel price is given with the aid of machine-learning. This may provide further insight into what a user may expect to pay, given historical data points.
