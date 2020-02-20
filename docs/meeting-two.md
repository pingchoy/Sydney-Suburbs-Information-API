# Meeting Two

## Points to be discussed/addressed

#### Is the group maintaining an effective communication channel for group work? (e.g., messaging, code repository)

Our primary communication channel is Slack (http://degenerates-global.slack.com/). Our channel is very active with all team members participating on a daily basis.

#### Is the group tracking the roles and tasks necessary for the group work? (i.e., is everybody fulfilling their tasks on time, and is there a mechanism in place to resolve problems?)

Yes, tasks are being tracking within our Github repository, see [tasks.md](tasks.md). Tasks are being completed on time by all members of the group. In terms of resolving problems, we are all in constant communication so anny issues are discussed amongst the group.

#### Is the implementation progressing towards the planned scenario? Does the group present a plan illustrating what has been done and what they are still working on? (e.g., in a Gant chart or even in a table showing the percentage of tasks.)

We are making excellent progress toward our scenario:

#### Completed Tasks

* **API Namespacing**: The API has been configured using Namespaces and is being run from a single app. This allows each member to work independently on their endpoints.
* **API Authentication**: Authentication has been implemented using JWT tokens and we have extended the tutorial functionality to include roles (`admin` and `user`) with a custom `decorator`. This is so certain endpoints can be restricted to certain users (eg, only admin can CRUD users). Passwords are stored as `SHA256` hashes instead of plaintext for additional security. 
* **API Querying, Sorting**: Query and sorting has been implemented for our endpoints 

`/resource?query=search+string&order=field&ascending=false`

* **API Pagination**: Pagination has been implemented for our long listings, it defaults to only displaying 25 records at a time and is customisable.

```javascript
{
    "results": [

    	//...

        {
            "id": 10000,
            "name": "Abbotsbury",
            "state": "NSW",
            "post_code": 2176,
            "latitude": -33.875,
            "longitude": 150.862,
            "sqkm": 4.9788,
            "population_male": 2076,
            "population_female": 2177,
            "population_total": 4253
        },

        //...
    ],
    "page": 1,
    "pages": 28,
    "per_page": 25,
    "total": 689
}
```

* **API Endpoints** that have been implemented:

Endpoint | Methods | Auth | Datasets
--- | --- | --- | ---
`/users(/[username])` | `GET` `POST`<br />`PUT` `DELETE` | Admin | -
`/suburbs(/[id])` | `GET` | User | [List of Sydney Suburbs](https://en.wikipedia.org/wiki/List_of_Sydney_suburbs)<br />[Google Maps Geocode API](https://developers.google.com/maps/documentation/geocoding)<br />[ABS SSC suburbs index](https://www.abs.gov.au/ausstats/)<br />[ABS Population data by suburb](https://datapacks.censusdata.abs.gov.au/datapacks/)
`/schools(/[id])` | `GET` | User | [NSW Public School Dataset](https://data.cese.nsw.gov.au/data/dataset/nsw-public-schools-master-dataset/resource/2ac19870-44f6-443d-a0c3-4c867f04c305)<br />[NSW Private School Dataset](https://data.cese.nsw.gov.au/data/dataset/nsw-non-government-school-locations-and-descriptions/resource/a5871783-7dd8-4b25-be9e-7d8b9b85422f)
`/train-stations(/[id])`<br />`/train-stations/nearest` | `GET` | User | [Public Transport - Location Facilities and Operators](https://opendata.transport.nsw.gov.au/dataset/public-transport-location-facilities-and-operators)
`/food(/[id])` | `GET` | User | [Zomato Resturaunt Listing API](https://developers.zomato.com/api)

### Outstanding Tasks

&#10003; | Task | Assigned 
:---: | :--- | :---
&nbsp; | API `/crime-rates` | Chris
&nbsp; | API `/property` | Harris
&nbsp; | API `/analytics` |  Alex
&nbsp; | API `/weather-forecast` |  Harris
&nbsp; | Unit testing | Chris
&nbsp; | Regression | Vidan
&nbsp; | Classification | Alex
&nbsp; | Swagger.io documentation |  Vidan
&nbsp; | Front-end mockup |  Chris
&nbsp; | Front-end functionality |  Ping

## Notes

- [ ] Each student separately should talk about their roles and how they have made progress
- [ ] Present your communication channel (Should be only in English)
- [ ] Present your code repository