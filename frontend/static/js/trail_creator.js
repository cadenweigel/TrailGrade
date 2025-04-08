// Initialize map
const map = L.map('map').setView([44.0521, -123.0897], 13); //Eugene's Lat/Long
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

let routePoints = [];  // Stores clicked points
let lastRouteLayer = null;  // Stores the last drawn route layer
let markers = [];  // Store draggable markers
let editMode = false;  // Track edit mode status

map.on('click', async function (e) {
    if (!editMode) {
        const elevation = await fetchElevation(e.latlng.lat, e.latlng.lng);
        const newMarker = addDraggableMarker(e.latlng);

        // Store elevation in (longitude, latitude, elevation) format
        routePoints.push([normalizeLongitude(e.latlng.lng), e.latlng.lat, elevation]);
        markers.push(newMarker);

        if (routePoints.length > 1) {
            updateRoute();
        }
    }
});

async function fetchElevation(lat, lng) {
    const url = `https://api.open-elevation.com/api/v1/lookup?locations=${lat},${lng}`;
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data.results[0].elevation;
    } catch (error) {
        console.error("Error fetching elevation:", error);
        return null;  // Return null if the API fails
    }
}

// Function to add a draggable marker at a given location
function addDraggableMarker(latlng) {
    const marker = L.marker(latlng, { draggable: true }).addTo(map);
    marker.on('dragend', updateRouteFromMarkers);
    return marker;
}

// Update route when a marker is dragged
async function updateRouteFromMarkers() {
    routePoints = await Promise.all(markers.map(async marker => {
        const latlng = marker.getLatLng();
        const elevation = await fetchElevation(latlng.lat, latlng.lng);
        return [normalizeLongitude(latlng.lng), latlng.lat, elevation];
    }));
    updateRoute();
}

// Function to normalize longitude values
function normalizeLongitude(lng) {
    return parseFloat((((lng + 180) % 360 + 360) % 360 - 180).toFixed(6));
}

// Function to draw straight lines between points
function updateRoute() {
    if (routePoints.length < 2) return;

    if (lastRouteLayer) {
        drawnItems.removeLayer(lastRouteLayer);  // Remove previous path
    }

    // Convert [lng, lat, elev] -> [lat, lng] for polylines
    const polylinePoints = routePoints.map(point => [point[1], point[0]]);

    const polyline = L.polyline(polylinePoints, { color: "blue" }).addTo(drawnItems);
    lastRouteLayer = polyline;
}

// Undo the last placed point
function undoLastPoint() {
    if (routePoints.length > 0) {
        routePoints.pop();
        const lastMarker = markers.pop();
        if (lastMarker) map.removeLayer(lastMarker);

        updateRoute();
    }
}

// Toggle edit mode
function toggleEditMode() {
    editMode = !editMode;
    markers.forEach(marker => marker.dragging[editMode ? "enable" : "disable"]());

    // Update button text
    const editButton = document.getElementById("editModeButton");
    if (editButton) {
        editButton.textContent = "Edit Mode: " + (editMode ? "ON" : "OFF");
    }
}

function exportGeoJSON() {
    const mapName = document.getElementById("mapName").value.trim();
    if (!mapName) {
        alert("Please enter a trail name before exporting.");
        return;
    }

    if (routePoints.length < 2) {
        alert("Not enough points to create a MultiLineString.");
        return;
    }

    // Keep elevation data in the GeoJSON format
    const lineCoordinates = routePoints.map(point => [point[0], point[1], point[2]]);

    const geojson = {
        type: "FeatureCollection",
        features: [
            {
                type: "Feature",
                geometry: {
                    type: "MultiLineString",
                    coordinates: [lineCoordinates] // Wrap in an array to follow MultiLineString structure
                },
                properties: {}
            }
        ]
    };

    fetch("/save_geojson", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: mapName.replace(/\s+/g, "_") + ".geojson", data: geojson })
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error("Error:", error));
}

function uploadGeoJSON() {
    const fileInput = document.getElementById('geojsonFile');
    if (!fileInput.files.length) {
        alert('Please select a file first.');
        return;
    }

    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onload = function(event) {
        try {
            const geojsonData = JSON.parse(event.target.result);
            const filename = file.name.replace(/\s+/g, '_');

            fetch('/upload_geojson', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename, data: geojsonData })
            })
            .then(response => response.json())
            .then(data => alert(data.message))
            .catch(error => console.error('Error:', error));
        } catch (e) {
            alert('Invalid GeoJSON file.');
        }
    };

    reader.readAsText(file);
}