# TrailGrade

TrailGrade is a Python-based system that analyzes hiking trail data to generate multidimensional difficulty ratings using various components like elevation, distance, etc. Users can view nearby trail data and difficulty ratings as well as create their own trails.

## Installation Instructions

### Requirements
- Python 3.8 or higher
- pip (Python package installer)

### Setting up the Environment

1. Create and activate a virtual environment:
```bash
python -m venv venv
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## How To Run TrailGrade

### Running the API

1. Ensure your virtual environment is activated.

2. Start the API server:
```bash
cd api && python api.py && cd ..
```

The API will be available at http://localhost:8000 by default.

### Running the Frontend

1. Ensure your virtual environment is activated.

2. Start the frontend server:
```bash
cd frontend && python app.py && cd ..
```

The frontend will be available at http://localhost:5000 by default.

## Using TrailGrade

[Installation Instructions](#installation-instructions)

[How To Run](#how-to-run-trailgrade)

### Viewing Trails

Users can view trails on the map by clicking on them or typing the name in on the search bar. They can  also filter the search bar to view trails by difficulty.

### Adding Trails

Users can add trails by clicking on "Add Trails" on the homepage and either manually create a trail on the map or upload a .geojson file.

## Directory Structure

```bash
.
├── LICENSE
├── README.md
├── .gitignore
├── .requirements.txt
├── docs/
├── .github/
│   ├── workflows/
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   ├── js/
│   ├── templates/
├── api/
├── core/
├── data/
├── storage/
│   └── trail_files/
│   └── user_uploads/
│   └── sample_trails/  
├── utils/
├── tests/

```
### Data Directory

This directory contains scripts for managing the `trails.db` database.

- **`delete_db.py`** - Deletes the current instance of `trails.db`.
- **`init_db.py`** - Initializes a `trails.db` database with necessary tables.
- **`add_trails.py`** - Searches for trails in `storage/trail_files` and adds them to the database.
- **`view_trails.py`** - Prints information on trails in the database to the terminal.

### Storage Directory

This directory contains trail files and user-uploaded data.

- **`trail_files/`** - Folder that stores `.geojson` files referenced by the database.
- **`user_uploads/`** - Folder that stores `.geojson` files uploaded by users.
- **`js_to_geojson.py`** - Converts `.js` files containing GeoJSON data to `.geojson` format.

### Trail Creator and Approval
#### Trail Creator

The trail creator allows you to create a trail by placing points. Consecutive points will be linked together via a straight line, so make sure to place points close together to keep the path on the trail. You can also upload existing `.geojson` files. There should be some you can upload in `/storage/sample_trails`.

#### Trail Approval

Navigating to [http://127.0.0.1:5000/approve_trails](http://127.0.0.1:5000/approve_trails) brings you to the trail approval page, where you can view submitted trails as well as approve or deny them.  

- **Approved trails** will be put in `/storage/trail_files`.  
- **To add them to the database**, run:  
  ```sh
  py add_trails.py

To see them in the app, you'll have to restart it.



## Authors

Jake Ferraro,
Caden Weigel,
Parker Stevenson,
Logan Sommerville,
Giovanni Mendoza Celestino
