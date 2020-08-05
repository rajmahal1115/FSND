### Capstone Project : Casting Agency

This project was the final project in the Udacity Nanodegree.The goal was to create the bankend for a Casting Agency application. This project combined everything that was taught in the previous projects which includes: creating a data model using SQLAlchemy, writing endpoints to do CRUD operations and having proper error handling, implementing RBAC,writing unit tests, hosting api on Heroku and making sure to follow PEP-8 coding standards.

### File Structure
- models.py : Contains the Movies and Actors models along with the gender class
- auth.py : Contains all of te authentication logic
- app.py : Contains all of the crud operation logic 
- test_app.py : Contains all of the unit tests for the project 
- requirements.txt : Contains all of the required packages for the project. You will need to pip install -r requirements.txt

### Roles
There are three roles that are set up inside of Auth0.
- Casting Assistant : Able to view actors and movies
- Casting Director : Able to do everything the casting agent can, add/delete actors and modify actors/movies
- Executive Producer : Able to do everything the previous 2 can and add/ delete movies

### Heroku

The app is hosted on Heroku and the link to access it is the following: 

### Testing
There is a test_app.py file which was was used to test the functionality of the endpoints in the test environment.Run it like you would any python file in the command prompt/terminal.

 Also there is a postman collection used to test the following endpoint in the production environment. 

GET '/actors/<int:id>'
GET '/actors'
GET '/movies'
DELETE '/actors/<int:id>' 
DELETE '/movies/<int:id>'
POST '/actors' 
POST '/movies' 
PATCH '/actors/<int:id>' 
PATCH '/movies/<int:id>'

### GET '/actors/<int:id>'
- Request argument: id of actor as an int 
- Roles able to perform action: Casting Assistant,Casting Director, Executive Producer
- Returns: The actor specified by the id 

{
    "actor": {
    "age": 65,
    "gender": "Male",
    "id": 1,
    "name": "Hugh Jackman"
  }
}

### GET '/actors'
- Request argument: None
- Roles able to perform action: Casting Assistant,Casting Director, Executive Producer
- Returns: All the actors 

{
  "actors": [
    {
      "age": 51,
      "gender": "Male",
      "id": 3,
      "name": "Hugh Jackman"
    },
    {
      "age": 51,
      "gender": "Female",
      "id": 4,
      "name": "Jennifer Aniston"
  ]
}

### GET '/movies'
- Request argument: None
- Roles able to perform action: Casting Assistant,Casting Director, Executive Producer
- Returns a list of movies

{
  "movies": [
    {
      "id": 3,
      "releaseDate": "Fri, 22 Jun 2001 00:00:00 GMT",
      "title": "Fast and Furious"
    },
    {
      "id": 4,
      "releaseDate": "Mon, 10 July 2020 00:00:00 GMT",
      "title": "The Old Guard"
    }
  ]
}

### DELETE '/actors/<int:id>'
- Request arguemnt : id of actor as int
- Roles able to perform action: Casting Director, Executive Producer
- Returns a success message if it successfully deleted the actor otherwise returns an error

{
  "status": "Success"
}

### DELETE '/movies/<int:id>'
-  Request arguemnt : id of a movie as int
- Roles able to perform action: Executive Producer
- Returns a success message if it successfully deleted the movie otherwise returns an error

{
  "status": "Success"
}


### POST '/actors' 
- Request arguemnt : None
- Roles able to perform action: Casting Director, Executive Producer
- Creates a new actor based on the information provided (name, age, gender) and returns a success message. If new actor is not created correctly then returns an error

{
  "status": "Success"
}

### POST '/movies'
- Request arguemnt : None
- Roles able to perform action: Executive Producer
- Creates a new movie based on the information provided (release date and title) and returns a success message. If new movie is not created correctly then returns an error

{
  "status": "Success"
}

### PATCH '/actors/<int:id>'
- Request arguemnt : id of a actor as int
- Roles able to perform the action: Casting Director, Executive Producer
- Modifies the actor based on the id provided. Returns a succcess message and the new modified actor's information. If there is an issue then it returns an error 

{
  "actor": {
    "age": 65,
    "gender": "Male",
    "id": 1,
    "name": "Test Actor"
  },
  "status": "Success"
}

### PATCH '/movies/<int:id>'
-  Request arguemnt : id of a movie as int
- Roles able to perform the action: Casting Director, Executive Producer
- - Modifies the movie based on the id provided. Returns a succcess message and the new modified movie's information. If there is an issue then it returns an error 

{
  "movie": {
    "id": 1,
    "releaseDate": "Sun, 17 Nov 1991 00:00:00 GMT",
    "title": "Test Movie"
  },
  "status": "Success"
}

### Error Handling







