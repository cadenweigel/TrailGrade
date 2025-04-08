document.addEventListener("DOMContentLoaded", function () {
    const trailListContainer = document.getElementById("trail-list");
    const searchInput = document.getElementById("search-trails");

    let hikingMap = L.map("map").setView([44.025, -123.025], 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(hikingMap);

    let allTrails = [];
    let trailMarkers = [];
    let activeMarker = null;

    async function loadTrails() {
        try {
            const response = await fetch("http://localhost:8000/api/trails"); // Assuming API runs on port 5000
            allTrails = await response.json();
            displayTrails(allTrails);
            addTrailsToMap(allTrails);
        } catch (error) {
            console.error("Error loading trails:", error);
        }
    }

    function displayTrails(trails) {
        trailListContainer.innerHTML = ""; 

        trails.forEach(trail => {
            // create difficulty color indicator with a gradient from green (1) to red (10)
            let difficultyColor = "#aaaaaa"; // default gray for unknown
            if (trail.difficulty_rating) {
                const rating = trail.difficulty_rating;
                // generate color on a gradient from green (1) to yellow (5) to red (10)
                switch(rating) {
                    case 1:
                    case 2:
                    case 3:
                        difficultyColor = 'rgb(0, 128, 0)';
                        break;
                    case 4:
                        difficultyColor = 'rgb(191, 223, 0)'
                        break;
                    case 5:
                        difficultyColor = 'rgb(255, 235, 0)'
                        break;
                    case 6:
                        difficultyColor = 'rgb(255, 190, 0)'
                        break;
                    case 7:
                        difficultyColor = 'rgb(255, 145, 0)'
                        break;
                    case 8:
                        difficultyColor = 'rgb(255, 102, 0)'
                        break;
                    case 9:
                        difficultyColor = 'rgb(255, 0, 0)'
                        break;
                    case 10:
                        difficultyColor = 'rgb(255,0,0)'
                        break;
                }   
            }

            // format trail difficulty with color coding and numeric display
            let difficultyDisplay = `
                <div class="difficulty-indicator" style="background-color: ${difficultyColor}; 
                        display: inline-block; width: 35px; height: 35px; border-radius: 50%; 
                        margin-right: 140px; color: white; font-weight: bold; line-height: 35px;
                        text-align: center; font-size: 22px;">
                    ${trail.difficulty_rating ? trail.difficulty_rating : "?"}
                </div>
            `;

            // add additional metrics if available
            let additionalMetrics = '';
            if (trail.cardio_intensity) {
                additionalMetrics += `
                    <div class="metrics-item">
                        <span>Cardio: ${trail.cardio_intensity}/10</span>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${trail.cardio_intensity * 10}%; 
                                    background-color: #5b9bd5;"></div>
                        </div>
                    </div>
                `;
            }
            
            if (trail.technical_difficulty) {
                additionalMetrics += `
                    <div class="metrics-item">
                        <span>Technical: ${trail.technical_difficulty}/10</span>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${trail.technical_difficulty * 10}%; 
                                    background-color: #ed7d31;"></div>
                        </div>
                    </div>
                `;
            }

            // add extra container if we have metrics
            let metricsContainer = '';
            if (additionalMetrics) {
                metricsContainer = `
                    <div class="trail-metrics">
                        ${additionalMetrics}
                    </div>
                `;
            }

            // create the trail item with all information
            const trailItem = document.createElement("div");
            trailItem.classList.add("trail-item");
            trailItem.innerHTML = `
                <h3>${trail.name}</h3>
                <div class="trail-basic-info">
                    <p style="padding-left: 10px;"><strong>Difficulty:</strong> ${difficultyDisplay}</p>
                    <p style="padding-right: 10px;"><strong>Length:</strong> ${trail.length.toFixed(1)} km</p>
                </div>
                ${metricsContainer}
                <div class="trail-actions">
                    <button class="view-trail" data-lat="${trail.location_lat}" data-lng="${trail.location_long}">View on Map</button>
                    <button class="view-path" data-trail="${encodeURIComponent(trail.name)}">View Trail Path</button>
                </div>
            `;
            trailListContainer.appendChild(trailItem);
        });

        document.querySelectorAll(".view-trail").forEach(button => {
            button.addEventListener("click", function () {
                const lat = parseFloat(this.dataset.lat);
                const lng = parseFloat(this.dataset.lng);

                // reset previous active marker
                if (activeMarker) {
                    activeMarker.setIcon(L.icon({
                        iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
                        shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                        shadowSize: [41, 41]
                    }));
                }

                // find marker for selected trail and highlight it
                for (let marker of trailMarkers) {
                    if (marker.trailData.location_lat === lat && marker.trailData.location_long === lng) {
                        // Set to red marker icon
                        marker.setIcon(L.icon({
                            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                            shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
                            iconSize: [25, 41],
                            iconAnchor: [12, 41],
                            popupAnchor: [1, -34],
                            shadowSize: [41, 41]
                        }));
                        activeMarker = marker;
                        break;
                    }
                }

                hikingMap.setView([lat, lng], 13);
            });
        });

        document.querySelectorAll(".view-path").forEach(button => {
            button.addEventListener("click", function () {
                const trailName = this.dataset.trail;
                window.location.href = `/trail_path/${trailName}`; // Redirect to trail path page
            });
        });
    }

    function addTrailsToMap(trails) {
        trailMarkers.forEach(marker => hikingMap.removeLayer(marker));
        trailMarkers = [];

        trails.forEach(trail => {
            let marker = L.marker([trail.location_lat, trail.location_long])
                .bindPopup(`<b>${trail.name}</b><br>${trail.difficulty} - ${trail.length.toFixed(1)} km`)
                .on('mouseover', function() {
                    this.openPopup();
                })
                .on('mouseout', function() {
                    this.closePopup();
                })
                .on('click', function() {
                    window.location.href = `/trail_path/${encodeURIComponent(trail.name)}`;
                })
            marker.trailData = trail;
            marker.addTo(hikingMap);
            trailMarkers.push(marker);

            
        });
    }

    searchInput.addEventListener("input", applyFilters);

    loadTrails();

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

    // Difficulty filter variables
    let minDifficulty = 1;
    let maxDifficulty = 10;
    let filterActive = false;

    // Filter button functionality
    const filterButton = document.getElementById('filter-button');
    const filterPopup = document.getElementById('filter-popup');
    const minDifficultySlider = document.getElementById('min-difficulty');
    const maxDifficultySlider = document.getElementById('max-difficulty');
    const difficultyValueDisplay = document.getElementById('difficulty-value');
    const applyFilterBtn = document.getElementById('apply-filter');
    const resetFilterBtn = document.getElementById('reset-filter');

    // Show/hide filter popup
    if (filterButton) {
        filterButton.addEventListener('click', function() {
            filterPopup.classList.toggle('hidden');
            
            // Close menu if open
            const menuDropdown = document.querySelector('.menu-dropdown');
            if (menuDropdown) {
                menuDropdown.remove();
            }
        });
    }

    // Update difficulty range display
    function updateDifficultyDisplay() {
        if (difficultyValueDisplay) {
            difficultyValueDisplay.textContent = `${minDifficultySlider.value}-${maxDifficultySlider.value}`;
        }
    }

    // Listen for slider changes
    if (minDifficultySlider && maxDifficultySlider) {
        minDifficultySlider.addEventListener('input', function() {
            // Ensure min doesn't exceed max
            if (parseInt(this.value) > parseInt(maxDifficultySlider.value)) {
                this.value = maxDifficultySlider.value;
            }
            updateDifficultyDisplay();
        });
        
        maxDifficultySlider.addEventListener('input', function() {
            // Ensure max doesn't go below min
            if (parseInt(this.value) < parseInt(minDifficultySlider.value)) {
                this.value = minDifficultySlider.value;
            }
            updateDifficultyDisplay();
        });
    }

    // Apply filter button
    if (applyFilterBtn) {
        applyFilterBtn.addEventListener('click', function() {
            minDifficulty = parseInt(minDifficultySlider.value);
            maxDifficulty = parseInt(maxDifficultySlider.value);
            filterActive = true;
            filterPopup.classList.add('hidden');
            
            // Apply filters and update display
            applyFilters();
        });
    }

    // Reset filter button
    if (resetFilterBtn) {
        resetFilterBtn.addEventListener('click', function() {
            minDifficultySlider.value = 1;
            maxDifficultySlider.value = 10;
            minDifficulty = 1;
            maxDifficulty = 10;
            filterActive = false;
            updateDifficultyDisplay();
            
            // Reset and show all trails
            applyFilters();
        });
    }

    // Function to apply all filters (search and difficulty)
    function applyFilters() {
        const searchQuery = searchInput.value.toLowerCase();
        
        const filteredTrails = allTrails.filter(trail => {
            // Text search filter
            const matchesSearch = trail.name.toLowerCase().includes(searchQuery);
            
            // Difficulty filter
            let matchesDifficulty = true;
            if (filterActive) {
                // Calculate display difficulty (same as in displayTrails)
                let calculatedDifficulty = null;
                if (trail.cardio_intensity && trail.technical_difficulty) {
                    calculatedDifficulty = Math.round(trail.cardio_intensity * 0.6 + trail.technical_difficulty * 0.4);
                } else if (trail.cardio_intensity) {
                    calculatedDifficulty = trail.cardio_intensity;
                } else if (trail.technical_difficulty) {
                    calculatedDifficulty = trail.technical_difficulty;
                } else if (trail.difficulty_rating) {
                    calculatedDifficulty = trail.difficulty_rating;
                }
                
                // If no difficulty available, exclude if filtering is active
                if (calculatedDifficulty === null) {
                    matchesDifficulty = false;
                } else {
                    matchesDifficulty = calculatedDifficulty >= minDifficulty && calculatedDifficulty <= maxDifficulty;
                }
            }
            
            return matchesSearch && matchesDifficulty;
        });
        
        displayTrails(filteredTrails);
        addTrailsToMap(filteredTrails);
    }

    // Update search input to use applyFilters
    searchInput.addEventListener("input", applyFilters);

    // Initialize difficulty display
    updateDifficultyDisplay();

});
