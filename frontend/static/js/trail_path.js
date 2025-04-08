document.addEventListener("DOMContentLoaded", async function () {
    const trailMap = L.map("trail-map").setView([44.5, -121.8], 12); // Default view

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(trailMap);

    // Hamburger menu functionality
    const menuButton = document.getElementById('menu-button');
    if (menuButton) {
        menuButton.addEventListener('click', function() {
            // Create menu dropdown
            const menuExists = document.querySelector('.menu-dropdown');
            
            if (menuExists) {
                menuExists.remove();
                return;
            }
            
            const menuDropdown = document.createElement('div');
            menuDropdown.className = 'menu-dropdown';
            menuDropdown.innerHTML = `
                <a href="/">Home</a>
                <a href="/trails">All Trails</a>
                <!-- Add more navigation links as needed -->
            `;
            
            // Position menu below the hamburger button
            const titleContainer = document.querySelector('.title-container');
            titleContainer.appendChild(menuDropdown);
            
            // Handle closing menu when clicking elsewhere
            const closeMenu = function(e) {
                if (!menuDropdown.contains(e.target) && e.target !== menuButton) {
                    menuDropdown.remove();
                    document.removeEventListener('click', closeMenu);
                }
            };
            
            // Small delay to prevent immediate closure
            setTimeout(() => {
                document.addEventListener('click', closeMenu);
            }, 100);
        });
    }

    // Extract trail name from the URL
    const trailName = document.getElementById("trail-name").innerText.trim();
    const detailsContainer = document.getElementById("trail-details");
    const difficultyContainer = document.getElementById("difficulty-ratings");

    try {
        const response = await fetch(`http://localhost:8000/api/trail_path/${encodeURIComponent(trailName)}`);
        const trailData = await response.json();

        if (!trailData || !trailData.coordinates) {
            detailsContainer.innerHTML = `<p><strong>Error:</strong> Trail details not found.</p>`;
            console.error("No trail path data found.");
            return;
        }

        // Display trail details in the sidebar
        detailsContainer.innerHTML = `
            <p><strong>Name:</strong> ${trailData.name}</p>
            <p><strong>Length:</strong> ${trailData.length ? trailData.length.toFixed(1) : "Unknown"} km</p>
            <p><strong>Max Elevation:</strong> ${trailData.max_elevation ?? "Unknown"} m</p>
            <p><strong>Min Elevation:</strong> ${trailData.min_elevation ?? "Unknown"} m</p>
            <p><strong>Elevation Gain:</strong> ${trailData.elevation_gain ?? "Unknown"} m</p>
            <p><strong>Elevation Loss:</strong> ${trailData.elevation_loss ?? "Unknown"} m</p>
        `;

        // display difficulty ratings (if available)
        if (trailData.difficulty) {
            const diff = trailData.difficulty;

            // helper function to generate color based on rating
            const getDifficultyColor = (rating) => {
                switch(rating) {
                    case 1:
                    case 2:
                    case 3:
                        return'rgb(0, 128, 0)';
                    case 4:
                        return 'rgb(191, 223, 0)'
                    case 5:
                        return 'rgb(255, 235, 0)'
                    case 6:
                        return 'rgb(255, 190, 0)'
                    case 7:
                        return 'rgb(255, 145, 0)'
                    case 8:
                        return 'rgb(255, 102, 0)'
                    case 9:
                        return 'rgb(255, 0, 0)'
                    case 10:
                        return 'rgb(255,0,0)'
                }  
            };

            // generate HTML for difficulty ratings
            difficultyContainer.innerHTML = `
                <h3>Difficulty Ratings</h3>
                <div class="difficulty-rating">
                    <div class="rating-label">Overall:</div>
                    <div class="rating-bar">
                        <div class="rating-fill" style="width: ${diff.overall_difficulty * 10}%; background-color: ${getDifficultyColor(diff.overall_difficulty)}"></div>
                        <div class="rating-text">${diff.overall_difficulty}/10</div>
                    </div>
                </div>
                <div class="difficulty-rating">
                    <div class="rating-label">Cardio Intensity:</div>
                    <div class="rating-bar">
                        <div class="rating-fill" style="width: ${diff.cardio_intensity * 10}%; background-color: ${getDifficultyColor(diff.cardio_intensity)}"></div>
                        <div class="rating-text">${diff.cardio_intensity}/10</div>
                    </div>
                </div>
                <div class="difficulty-rating">
                    <div class="rating-label">Technical Difficulty:</div>
                    <div class="rating-bar">
                        <div class="rating-fill" style="width: ${diff.technical_difficulty * 10}%; background-color: ${getDifficultyColor(diff.technical_difficulty)}"></div>
                        <div class="rating-text">${diff.technical_difficulty}/10</div>
                    </div>
                </div>`;

            // add other difficulty ratings if they exist and are not null
            if (diff.accessibility && diff.accessibility !== null) {
                difficultyContainer.innerHTML += `
                <div class="difficulty-rating">
                    <div class="rating-label">Accessibility:</div>
                    <div class="rating-bar">
                        <div class="rating-fill" style="width: ${diff.accessibility * 10}%; background-color: ${getDifficultyColor(diff.accessibility)}"></div>
                        <div class="rating-text">${diff.accessibility}/10</div>
                    </div>
                </div>`;
            }
            
            if (diff.weather_vulnerability && diff.weather_vulnerability !== null) {
                difficultyContainer.innerHTML += `
                <div class="difficulty-rating">
                    <div class="rating-label">Weather Vulnerability:</div>
                    <div class="rating-bar">
                        <div class="rating-fill" style="width: ${diff.weather_vulnerability * 10}%; background-color: ${getDifficultyColor(diff.weather_vulnerability)}"></div>
                        <div class="rating-text">${diff.weather_vulnerability}/10</div>
                    </div>
                </div>`;
            }
        }

        // Convert coordinates to Leaflet-friendly format
        const trailCoords = trailData.coordinates.map(coord => [coord[1], coord[0]]); // Convert [lon, lat] to [lat, lon]

        // Draw trail path on the map
        L.polyline(trailCoords, { color: "blue", weight: 4 }).addTo(trailMap);

        // add elevation marker points if elevation data is available
        if (trailData.coordinates.some(coord => coord.length > 2)) {
            for (let i = 0; i < trailCoords.length; i += Math.max(1, Math.floor(trailCoords.length / 20))) {
                const coord = trailCoords[i];
                const originalCoord = trailData.coordinates[i];
                if (originalCoord.length > 2) {
                    const elevation = originalCoord[2];
                    L.circleMarker(coord, {
                        radius: 4,
                        color: '#ff7800',
                        fill: true,
                        fillOpacity: 0.8
                    }).bindPopup(`Elevation: ${elevation} m`).addTo(trailMap);
                }
            }
        }

        // Fit map to the trail bounds
        trailMap.fitBounds(trailCoords);

        // add elevation profile if the container exists
        const elevationProfileContainer = document.getElementById("elevation-profile");
        if (elevationProfileContainer && trailData.coordinates.some(coord => coord.length > 2)) {
            createElevationProfile(trailData.coordinates, elevationProfileContainer);
        }

    } catch (error) {
        detailsContainer.innerHTML = `<p><strong>Error:</strong> Failed to load trail details.</p>`;
        console.error("Error fetching trail path data:", error);
    }
});

// function to create elevation profile chart
function createElevationProfile(coordinates, container) {
    // extract distances and elevations
    const elevations = [];
    const distances = [];
    let totalDistance = 0;
    
    for (let i = 0; i < coordinates.length; i++) {
        const coord = coordinates[i];
        if (coord.length > 2) {
            elevations.push(coord[2]);
            
            // calculate distance (simple accumulation for visualization purposes)
            if (i > 0) {
                const prevCoord = coordinates[i-1];
                // simple euclidean distance for demonstration
                const dist = Math.sqrt(
                    Math.pow(coord[0] - prevCoord[0], 2) + 
                    Math.pow(coord[1] - prevCoord[1], 2)
                ) * 111000; // very rough conversion to meters (111km per degree)
                totalDistance += dist;
            }
            distances.push(totalDistance / 1000); // convert to km
        }
    }
    
    // create the chart
    const ctx = document.createElement('canvas');
    container.appendChild(ctx);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: distances,
            datasets: [{
                label: 'Elevation (m)',
                data: elevations,
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.2)',
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Distance (km)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Elevation (m)'
                    }
                }
            }
        }
    });
}