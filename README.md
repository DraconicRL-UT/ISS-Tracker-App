# The ISS Tracker Flask

## Software Diagram
Here is a software diagram to describe the software hierarchy and interconnections. See below:
[Software Diagram](diagram.png)

<picture>
 <img alt="Software diagram below: " src="https://github.com/DraconicRL-UT/COE-332/blob/main/homework05/diagram.png">
</picture>

As seen, the Dockerfile is used to generate a containerized flask
which has the iss_tracker application with the routes shown in the
diagram. Included in the container is a test_iss_tracker.py
exectutable that tests the internal functions of the iss_tracker
executable (including the routes).

## Directory Overview
> ISS-Tracker-App/
> - Dockerfile
> - docker-compose.yml
> - requirements.txt
> - iss_tracker.py
> - test_iss_tracker.py
> - diagram.png
> - README.md

1. Dockerfile: Provides instructions for docker to create a 
containerized app image for the ISS-Tracker app. Needs to be called to
build then run the container.
2. docker-compose.yml: Also provides instructions for docker to create
a containerized app image for the ISS-Tracker app, but automates the
build and run process
3. requirements.txt: Lists the required version dependencies for the 
python libraries used in this app
4. iss_tracker.py: The primary python script that pulls the ISS state
vector data from the ISS website (more details in next section) and 
gives users routes to call functions that access data or data subsets of interest regarding the ISSS.
5. test_iss_tracker.py: The unit test file that tests all the routes 
and functions used in the iss_tracker.py python script.
6. diagram.png: The software diagram for this project.

## Instructions For Container Creation With Docker
### Bulding Container
To build the container image from a Dockerfile, ensure docker is 
installed on location newtwork (if on a server) or laptop, and that
the current directory has the Dockerfile along with the dependent 
files (2 scripts total: the iss_tracker.py and test_iss_tracker.py
python script files). Then run the docker build command along with the
desired image name and tag. For example, if the username is "user",
the desired filename is "name", tag is "1.0", run this in command 
line: 
``` 
docker build -t user/name:1.0 .
``` 
This will build/"create" the docker container image. 

Note that the container will pull the most recent data relating to the
location of the ISS location (in statevector format). This is located
at: [link to download ISS dataset](https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml). This was 
pulled from the official ISS website: [here](https://spotthestation.nasa.gov/trajectory_data.cfm). Note that the scripts are written to do 
this inside the code, so there is no need to store a local copy on the
local computer or wget a copy. 

### Running The Container App (using Dockerfile)
To run the image, simply call the docker run command on command line
like so: 
```
docker run --rm -it username/image_name:image_version
```
If an interactive interface is not desired, omit the "-it"). To run 
the containerized code for the test function, simply move into the 
code folder then call the test function name or call pytest if the app
was run interactively. For the iss_tracker code, you will need two 
active instances, one to run the application, and another to navigate
the rest api. 

To run the image in the background, excute the same command as 
mentioned in the previous section, but omit the "-it" tag and replace
it with a "-d" (for background run) tag instead. Like so:
```
docker run --rm -d username/image_name:image_version
```

### Alternative Method of Running Container (using docker-compose)
To use the docker-compose.yml file to automate the building and 
running of the containerized code, use this command in command line:
```
docker-compose up -d
```
Note that the "-d" tag is for this to run the app in the background,
but if it is undesired the "-d" tag can be ommitted and the app will
need to have 2 active instances running (one to run the server, and 
another to curl the routes for the desired outputs). 

## Details On Usage Of The Container
For the iss_tracker.py file, when running the application, the 
"home"-page can be accessed with:
```
curl localhost:5000/
```
This home page will print out some simply summary statistics about the ISS's current 15 day period. To view the comments about the ISS data use:
```
curl localhost:5000/comment
```
To view the headers about the ISS data use:
```
curl localhost:5000/header
```
To view the metadata of the ISS use:
```
curl localhost:5000/metadata
```
To access the list for the ISS statevector and epoch at each timestep (every 4 minutes across a 15 day period)
use:
```
curl localhost:5000/epochs
```
To alternatively, pull up the statevector for a specific time step, 
adjust the route to be:
``` 
curl localhost:5000/epochs/<specific_epoch>
```
For example, if we wanted to look at the state vector of the intial 
time (if it was 2024-050T14:25:00.000Z or 2024 Feb 19th 2:45:00pm UTC)
, it could be accessed with: 
```
curl 'localhost:5000/epochs/2024-050T14:25:00.000Z'
``` 
Conversely, to access the last time step (in other words the current 
time as of right "now"), use: 
```
curl localhost:5000/now
```
To output a queried list of the epochs, for example with an offset of one, run this in command line: 
```
curl 'localhost:5000/epochs?offset=1'
```
Alterantively, to limit the query size to only 20 entries with no 
offset, use: 
```
curl 'localhost:5000/epochs?limit=20'
```
To limit to the first 20 items after an offset of 5, enter this in 
command line: 
```
curl 'localhost:5000/epochs/limit=20&offset=5'
```
To find the speed of the ISS at a particular epoch, say an epoch of 
the same time as before (2024-050T14:25:00.000Z), input this into 
the command line: 
```
curl 'localhost:5000/epochs/2024-050T14:25:00.000Z/speed'
```

## Citations & References
1. [COE 332 Course Readthedocs website](https://coe-332-sp24.readthedocs.io/en/latest/homework/midterm.html)
2. [ISS data (explanation of data)](https://spotthestation.nasa.gov/trajectory_data.cfm)
3. [Download ISS statevector data](https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml)
4. [Astropy documentation on Earth Location object](https://docs.astropy.org/en/stable/api/astropy.coordinates.EarthLocation.html)
5. [Reference Implementation of astropy](https://stackoverflow.com/questions/78097446/how-do-i-use-astropy-to-transform-coordinates-from-j2000-to-lat-lon-and-altitu)
6. [Geopy documentation](https://geopy.readthedocs.io/en/stable/#installation)



