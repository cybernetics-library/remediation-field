# Remediation Field

~~The CyberCon Simulation (CyberSym) creates a feedback loop between conference speakers and attendees, framing the conference itself as a cybernetic system.~~

This is based off of https://github.com/cybernetics-conference/cybersym.

## Setup


### Api

`python app.py`.

When running for production, this is run using gunicorn and a virtualenv with pm2 using the shell script `start_library_api.sh`.

Endpoints:

- `/plot/link` [POST]: Link a plot to a book. Needs `book_id`, `plot_id`, `station_id`, `timestamp`.
- `/plot/unlink` [POST]: Unlink a plot and a book. Needs `book_id`, `plot_id`, `station_id`, `timestamp`.
- `/plot/rename` [POST]: Rename a plot. Needs `book_id`, `plot_id`, `station_id`, `timestamp`.
- `/plot/names` [GET]: Return all the names of the plots
- `/plots` [GET]: Return all of the plots and their names and links
- `/plots/<plotid>` [GET]: Return only one of the plots and their names and links
- `/books` [GET]: Return all of the books and their names and links
- `/books/<bookid>` [GET]: Return only one of the books and their names and links




### Visualizations 

In the `viz/` directory:
```
npm install -d
npm start
```

Then visit `localhost:8081/planet`, etc.

## Architecture

`viz/` directory holds all the node & THREE.js visualizations. 

`app/` directory holds the server-side API with endpoints. Global API is `https://library.cybernetics.social`. Much of the logic can happen in here.

## Reference images

![simulation_architecture_diagram](https://github.com/cybernetics-conference/cybersym/blob/master/repo_images/simulation_architecture_diagram.jpg)
![simulation_diagram](https://github.com/cybernetics-conference/cybersym/blob/master/repo_images/simulation_diagram.jpg)
