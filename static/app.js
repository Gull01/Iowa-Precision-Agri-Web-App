// API Base URL
const API_BASE = 'http://localhost:8000/api';

// Initialize map
let map;
let drawnItems;
let selectedFarm = null;
let satelliteLayersControl = null;  // Layer control object
let ndviOverlays = [];              // Store NDVI overlay layers
let activeIowaLayers = [];          // Track active Iowa layers for AI insights

// Initialize the map
function initMap() {
    // Set initial view to Iowa
    map = L.map('map').setView([41.938403, -93.389831], 7);
    
    // Initialize base maps only (Street, Satellite, Topography)
    const baseMaps = {
        "Street Map": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }),
        "Satellite Map": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 19,
            attribution: '© ESRI'
        }),
        "Topography Map": L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            maxZoom: 17,
            attribution: '© OpenTopoMap contributors'
        })
    };
    
    // Add default base map
    baseMaps["Street Map"].addTo(map);
    
    // Add simple base map control
    L.control.layers(baseMaps, null, {
        position: 'topright',
        collapsed: false
    }).addTo(map);
    
    // Initialize Iowa local data layers (LULC, climate, vegetation, etc.)
    initializeIowaLocalLayers(map);
    
    // Initialize AI Insights
    if (typeof initializeAIInsights === 'function') {
        initializeAIInsights(map);
        console.log('✅ AI Insights initialized');
        
        // Attach click handler for AI insights
        if (typeof attachAIClickHandler === 'function') {
            attachAIClickHandler(map);
            console.log('✅ AI click handler attached');
        }
    }
    
    // Initialize drawn items layer
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
    
    // Add drawing controls
    const drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: {
            polygon: true,
            polyline: false,
            rectangle: true,
            circle: false,
            marker: true,
            circlemarker: false
        }
    });
    map.addControl(drawControl);
    
    // Handle drawing events
    map.on(L.Draw.Event.CREATED, function(event) {
        const layer = event.layer;
        drawnItems.addLayer(layer);
        
        // Get GeoJSON of drawn shape
        const geoJSON = layer.toGeoJSON();
        console.log('Drawn shape:', geoJSON);
        
        // You can now associate this with a field
        if (event.layerType === 'polygon' || event.layerType === 'rectangle') {
            // This could trigger field creation or update
            alert('Field boundary drawn! Use this to create or update a field.');
        }
    });
}

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE}/statistics/dashboard`);
        const data = await response.json();
        
        document.getElementById('totalFarms').textContent = data.total_farms;
        document.getElementById('totalFields').textContent = data.total_fields;
        document.getElementById('totalArea').textContent = data.total_area_hectares.toFixed(1);
        document.getElementById('totalSensors').textContent = data.total_sensors;
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

// Load farms
async function loadFarms() {
    try {
        const response = await fetch(`${API_BASE}/farms/`);
        const farms = await response.json();
        
        const farmsList = document.getElementById('farmsList');
        const farmSelect = document.getElementById('fieldFarmId');
        
        farmsList.innerHTML = '';
        farmSelect.innerHTML = '<option value="">Select a farm...</option>';
        
        if (farms.length === 0) {
            farmsList.innerHTML = '<p style="color: #666; font-size: 14px;">No farms yet. Create one to get started!</p>';
            return;
        }
        
        farms.forEach(farm => {
            // Add to list
            const farmDiv = document.createElement('div');
            farmDiv.className = 'field-item';
            farmDiv.innerHTML = `
                <div style="flex: 1; cursor: pointer;" onclick="selectFarm(${JSON.stringify(farm).replace(/"/g, '&quot;')})">
                    <strong>${farm.name}</strong><br>
                    <small>Owner: ${farm.owner}</small><br>
                    <small>${farm.location || 'No location'}</small>
                </div>
                <button onclick="deleteFarm(${farm.id}, '${farm.name}'); event.stopPropagation();" 
                        style="background: #dc3545; color: white; border: none; padding: 6px 12px; 
                               border-radius: 4px; cursor: pointer; font-size: 12px; margin-left: 8px;"
                        title="Delete farm">
                    🗑️ Delete
                </button>
            `;
            farmDiv.style.display = 'flex';
            farmDiv.style.alignItems = 'center';
            farmsList.appendChild(farmDiv);
            
            // Add to select dropdown
            const option = document.createElement('option');
            option.value = farm.id;
            option.textContent = farm.name;
            farmSelect.appendChild(option);
            
            // Add marker to map if coordinates exist
            if (farm.latitude && farm.longitude) {
                const marker = L.marker([farm.latitude, farm.longitude])
                    .bindPopup(`
                        <strong>${farm.name}</strong><br>
                        Owner: ${farm.owner}<br>
                        Area: ${farm.total_area || 'N/A'} ha
                    `)
                    .addTo(map);
            }
        });
    } catch (error) {
        console.error('Error loading farms:', error);
    }
}

// Select a farm
function selectFarm(farm) {
    selectedFarm = farm;
    if (farm.latitude && farm.longitude) {
        map.setView([farm.latitude, farm.longitude], 13);
    }
    loadFields(farm.id);
    loadWeatherForecast(farm.id);
}

// Load fields
async function loadFields(farmId = null) {
    try {
        const url = farmId ? `${API_BASE}/fields/?farm_id=${farmId}` : `${API_BASE}/fields/`;
        const response = await fetch(url);
        const fields = await response.json();
        
        const fieldsList = document.getElementById('fieldsList');
        fieldsList.innerHTML = '';
        
        if (fields.length === 0) {
            fieldsList.innerHTML = '<p style="color: #666; font-size: 14px;">No fields yet.</p>';
            return;
        }
        
        // Clear existing field layers and NDVI overlays
        drawnItems.clearLayers();
        ndviOverlays.forEach(overlay => map.removeLayer(overlay));
        ndviOverlays = [];
        
        fields.forEach(field => {
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'field-item';
            fieldDiv.innerHTML = `
                <div style="flex: 1; cursor: pointer;" onclick="viewFieldAnalysis(${field.id})">
                    <strong>${field.name}</strong><br>
                    <small>Crop: ${field.crop_type || 'N/A'} | ${field.area || 'N/A'} ha</small>
                </div>
                <button onclick="deleteField(${field.id}, '${field.name}'); event.stopPropagation();" 
                        style="background: #dc3545; color: white; border: none; padding: 6px 12px; 
                               border-radius: 4px; cursor: pointer; font-size: 12px; margin-left: 8px;"
                        title="Delete field">
                    🗑️ Delete
                </button>
            `;
            fieldDiv.style.display = 'flex';
            fieldDiv.style.alignItems = 'center';
            fieldsList.appendChild(fieldDiv);
            
            // Draw field boundary if geometry exists (wrapped in async IIFE)
            if (field.geometry) {
                (async () => {
                    try {
                        const geojson = JSON.parse(field.geometry);
                        
                        // Get NDVI data for color coding
                        let ndviColor = '#2c5530';  // Default green
                        let ndviValue = null;
                        
                        try {
                            const ndviResponse = await fetch(`${API_BASE}/satellite/instant-ndvi/${field.id}?days_back=30`);
                            const ndviData = await ndviResponse.json();
                        
                        if (ndviData.estimated_ndvi !== undefined) {
                            ndviValue = ndviData.estimated_ndvi;
                            ndviColor = getNDVIColor(ndviValue);
                            
                            // Create NDVI overlay
                            const ndviOverlay = L.geoJSON(geojson, {
                                style: {
                                    color: ndviColor,
                                    weight: 3,
                                    fillColor: ndviColor,
                                    fillOpacity: 0.4
                                }
                            }).bindPopup(`
                                <div style="min-width: 220px;">
                                    <h4 style="margin: 0 0 10px 0;">${field.name}</h4>
                                    <div style="margin: 8px 0;">
                                        <strong>Crop:</strong> ${field.crop_type || 'N/A'}<br>
                                        <strong>Area:</strong> ${field.area || 'N/A'} ha
                                    </div>
                                    <hr style="margin: 10px 0; border: none; border-top: 1px solid #ddd;">
                                    <div style="text-align: center; margin: 10px 0;">
                                        <div style="font-size: 12px; color: #666; margin-bottom: 4px;">🛰️ NDVI</div>
                                        <div style="font-size: 28px; font-weight: bold; color: ${ndviColor};">
                                            ${ndviValue.toFixed(3)}
                                        </div>
                                        <div style="margin: 8px 0;">
                                            <strong>${ndviData.health_status}</strong>
                                        </div>
                                        <div style="font-size: 11px; color: #666;">
                                            ${new Date(ndviData.latest_date).toLocaleDateString()}<br>
                                            ${ndviData.scenes_found} satellite scenes
                                        </div>
                                    </div>
                                    <button onclick="viewFieldAnalysis(${field.id})" 
                                            style="width: 100%; padding: 8px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; margin-top: 8px;">
                                        View Full Analysis
                                    </button>
                                </div>
                            `);
                            
                            ndviOverlay.addTo(drawnItems);
                            ndviOverlays.push(ndviOverlay);
                        }
                    } catch (e) {
                        console.warn('Could not load NDVI for field', field.id, e);
                        // Fall back to basic boundary
                        const basicLayer = L.geoJSON(geojson, {
                            style: {
                                color: '#2c5530',
                                weight: 2,
                                fillOpacity: 0.3
                            }
                        }).bindPopup(`
                            <strong>${field.name}</strong><br>
                            Crop: ${field.crop_type || 'N/A'}<br>
                            Area: ${field.area || 'N/A'} ha
                        `).addTo(drawnItems);
                    }
                } catch (e) {
                    console.error('Error parsing field geometry:', e);
                }
                })(); // Close async IIFE
            }
        });
    } catch (error) {
        console.error('Error loading fields:', error);
    }
}

// Delete farm function
async function deleteFarm(farmId, farmName) {
    if (!confirm(`Are you sure you want to delete farm "${farmName}"?\n\nThis will also delete all fields associated with this farm.\n\nThis action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/farms/${farmId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert(`Farm "${farmName}" deleted successfully!`);
            
            // Clear selected farm
            currentFarm = null;
            
            // Reload farms and fields
            await loadFarms();
            await loadFields();
            await loadDashboardStats();
        } else {
            const error = await response.json();
            alert(`Error deleting farm: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error deleting farm:', error);
        alert('Failed to delete farm. Please try again.');
    }
}

// Delete field function
async function deleteField(fieldId, fieldName) {
    if (!confirm(`Are you sure you want to delete field "${fieldName}"?\n\nThis action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/fields/${fieldId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert(`Field "${fieldName}" deleted successfully!`);
            
            // Clear analysis section if this field was displayed
            const analysisSection = document.getElementById('analysisSection');
            if (analysisSection) {
                analysisSection.style.display = 'none';
            }
            
            // Reload fields and dashboard
            await loadFields();
            await loadDashboardStats();
        } else {
            const error = await response.json();
            alert(`Error deleting field: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error deleting field:', error);
        alert('Failed to delete field. Please try again.');
    }
}

// View field analysis
async function viewFieldAnalysis(fieldId) {
    try {
        const response = await fetch(`${API_BASE}/analysis/field/${fieldId}`);
        const analysis = await response.json();
        
        const analysisSection = document.getElementById('analysisSection');
        const analysisContent = document.getElementById('analysisContent');
        
        analysisSection.style.display = 'block';
        
        const healthClass = {
            'Excellent': 'health-excellent',
            'Good': 'health-good',
            'Fair': 'health-fair',
            'Poor': 'health-poor'
        }[analysis.health_status] || '';
        
        analysisContent.innerHTML = `
            <h3 style="color: #1e7e34; margin-bottom: 12px;">${analysis.field_name}</h3>
            <p><strong>Crop:</strong> ${analysis.crop_type}</p>
            <p><strong>Area:</strong> ${analysis.area} ha</p>
            
            <div style="margin: 15px 0;">
                <strong>Health Status:</strong>
                <span class="health-indicator ${healthClass}"></span>
                ${analysis.health_status}
            </div>
            
            ${analysis.avg_ndvi ? `<p><strong>NDVI:</strong> ${analysis.avg_ndvi.toFixed(3)}</p>` : ''}
            
            <div style="margin: 15px 0;">
                <strong>Soil Quality:</strong><br>
                <small>
                    pH: ${analysis.soil_quality.ph || 'N/A'} |
                    N: ${analysis.soil_quality.nitrogen || 'N/A'} ppm |
                    P: ${analysis.soil_quality.phosphorus || 'N/A'} ppm |
                    K: ${analysis.soil_quality.potassium || 'N/A'} ppm
                </small>
            </div>
            
            <div style="margin: 15px 0;">
                <strong>Recommendations:</strong>
                <ul style="margin: 5px 0; padding-left: 20px; font-size: 13px;">
                    ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
            
            ${analysis.last_monitoring ? 
                `<small>Last monitored: ${new Date(analysis.last_monitoring).toLocaleDateString()}</small>` : 
                '<small>No monitoring data available</small>'}
        `;
        
        // Load satellite data for this field
        loadSatelliteData(fieldId);
        
    } catch (error) {
        console.error('Error loading field analysis:', error);
    }
}

// Farm Modal Functions
function openFarmModal() {
    document.getElementById('farmModal').style.display = 'block';
}

function closeFarmModal() {
    document.getElementById('farmModal').style.display = 'none';
    document.getElementById('farmForm').reset();
}

// Field Modal Functions
function openFieldModal() {
    if (document.getElementById('fieldFarmId').options.length <= 1) {
        alert('Please create a farm first!');
        return;
    }
    document.getElementById('fieldModal').style.display = 'block';
}

function closeFieldModal() {
    document.getElementById('fieldModal').style.display = 'none';
    document.getElementById('fieldForm').reset();
}

// Create Farm
document.getElementById('farmForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const farmData = {
        name: document.getElementById('farmName').value,
        owner: document.getElementById('farmOwner').value,
        location: document.getElementById('farmLocation').value || null,
        latitude: parseFloat(document.getElementById('farmLat').value) || null,
        longitude: parseFloat(document.getElementById('farmLon').value) || null,
        total_area: parseFloat(document.getElementById('farmArea').value) || null
    };
    
    try {
        const response = await fetch(`${API_BASE}/farms/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(farmData)
        });
        
        if (response.ok) {
            alert('Farm created successfully!');
            closeFarmModal();
            loadFarms();
            loadDashboardStats();
        } else {
            const error = await response.json();
            alert('Error creating farm: ' + JSON.stringify(error));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error creating farm');
    }
});

// Create Field
document.getElementById('fieldForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fieldData = {
        farm_id: parseInt(document.getElementById('fieldFarmId').value),
        name: document.getElementById('fieldName').value,
        crop_type: document.getElementById('fieldCropType').value || null,
        area: parseFloat(document.getElementById('fieldArea').value) || null,
        soil_type: document.getElementById('fieldSoilType').value || null,
        soil_ph: parseFloat(document.getElementById('fieldSoilPH').value) || null,
        soil_nitrogen: parseFloat(document.getElementById('fieldNitrogen').value) || null,
        soil_phosphorus: parseFloat(document.getElementById('fieldPhosphorus').value) || null,
        soil_potassium: parseFloat(document.getElementById('fieldPotassium').value) || null
    };
    
    try {
        const response = await fetch(`${API_BASE}/fields/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(fieldData)
        });
        
        if (response.ok) {
            const field = await response.json();
            alert('Field created successfully!');
            closeFieldModal();
            loadFields(fieldData.farm_id);
            loadDashboardStats();
        } else {
            const error = await response.json();
            alert('Error creating field: ' + JSON.stringify(error));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error creating field');
    }
});

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Initialize app on load
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadDashboardStats();
    loadFarms();
    loadFields();
});

// Load weather forecast
async function loadWeatherForecast(farmId) {
    try {
        const weatherSection = document.getElementById('weatherSection');
        const weatherContent = document.getElementById('weatherContent');
        
        weatherSection.style.display = 'block';
        weatherContent.innerHTML = '<div class="loading">Loading weather...</div>';
        
        const response = await fetch(`${API_BASE}/weather/${farmId}/forecast?days=5`);
        const data = await response.json();
        
        let html = `
            <div style="margin-bottom: 12px; padding: 12px; background: #e8f5e9; border-radius: 8px;">
                <strong style="color: #1e7e34;">📍 ${data.farm_name}</strong><br>
                <small style="color: #666;">5-Day Agricultural Forecast</small>
            </div>
        `;
        
        data.daily_forecast.slice(0, 5).forEach(day => {
            const date = new Date(day.date);
            const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            
            html += `
                <div class="forecast-day">
                    <div class="forecast-date">${dateStr}</div>
                    <div class="forecast-temps">
                        🌡️ ${Math.round(day.temperature_min)}°C - ${Math.round(day.temperature_max)}°C
                    </div>
                    <div class="forecast-temps">
                        🌧️ ${day.precipitation_mm} mm | 💨 ${Math.round(day.wind_speed_max)} km/h
                    </div>
                    ${day.recommendations && day.recommendations.length > 0 ? 
                        `<div class="forecast-recommendation">${day.recommendations[0]}</div>` : ''}
                </div>
            `;
        });
        
        html += `
            <div style="margin-top: 12px; padding: 8px; text-align: center; font-size: 11px; color: #999;">
                Data from Open-Meteo (Free API)
            </div>
        `;
        
        weatherContent.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading weather:', error);
        document.getElementById('weatherContent').innerHTML = 
            '<div style="padding: 12px; text-align: center; color: #dc3545;">Weather data unavailable</div>';
    }
}

// Load satellite NDVI data for field
async function loadSatelliteData(fieldId) {
    try {
        const satelliteSection = document.getElementById('satelliteSection');
        const satelliteContent = document.getElementById('satelliteContent');
        
        satelliteSection.style.display = 'block';
        satelliteContent.innerHTML = '<div class="loading">⚡ Loading instant satellite data...</div>';
        
        // Use NEW instant satellite endpoint - NO WAITING!
        const response = await fetch(`${API_BASE}/satellite/instant-ndvi/${fieldId}?days_back=30`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to load satellite data');
        }
        
        if (data.scenes_found && data.scenes_found > 0) {
            const ndviValue = data.estimated_ndvi.toFixed(3);
            const latestDate = new Date(data.latest_date).toLocaleDateString();
            const cloudCover = data.latest_cloud_cover.toFixed(1);
            
            satelliteContent.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 14px; color: #666; margin-bottom: 8px;">⚡ INSTANT Satellite NDVI</div>
                    <div class="ndvi-value">${ndviValue}</div>
                    <div style="margin: 12px 0;">
                        <span class="health-indicator health-${data.health_status.toLowerCase()}"></span>
                        <strong>${data.health_status}</strong>
                    </div>
                    <div style="margin: 12px 0;">
                        <span class="trend-badge trend-stable">
                            ✅ ${data.scenes_found} scenes analyzed
                        </span>
                    </div>
                </div>
                
                <div class="satellite-info">
                    <strong>🛰️ Sentinel-2 (FREE - No Waiting!)</strong><br>
                    <small>
                        Latest Date: ${latestDate}<br>
                        Cloud Coverage: ${cloudCover}%<br>
                        Resolution: 10 meters<br>
                        Source: Microsoft Planetary Computer<br>
                        <strong style="color: #10b981;">✅ Instant Historical Data</strong>
                    </small>
                </div>
                
                <div style="margin-top: 16px; padding: 12px; background: #f0fdf4; border-radius: 8px; border-left: 4px solid #10b981;">
                    <small style="color: #166534;">
                        <strong>💡 Pro Tip:</strong> Data is instant! No 2-3 day waiting period. 
                        FREE access via Microsoft Planetary Computer.
                    </small>
                </div>
            `;
        } else {
            satelliteContent.innerHTML = `
                <div style="padding: 16px; text-align: center;">
                    <p style="color: #666; margin-bottom: 12px;">
                        ⚠️ ${data.message || 'No satellite imagery found'}
                    </p>
                    <small style="color: #999;">
                        Try increasing the time range. This field may have high cloud coverage.
                    </small>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error loading satellite data:', error);
        document.getElementById('satelliteContent').innerHTML = `
            <div style="padding: 16px; text-align: center;">
                <p style="color: #dc2626;">❌ Error loading satellite data</p>
                <small style="color: #999;">${error.message}</small>
            </div>
        `;
    }
}

// Register field for satellite monitoring
async function registerFieldForSatellite(fieldId) {
    if (!confirm('Register this field for satellite monitoring? (Sentinel-2 NDVI data will be available in 2-3 days)')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/agromonitoring/register-field/${fieldId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            alert('✅ Field registered for satellite monitoring!\n\n' + result.note);
            loadSatelliteData(fieldId);
        } else {
            const error = await response.json();
            alert('Error: ' + error.detail);
        }
    } catch (error) {
        console.error('Error registering field:', error);
        alert('Failed to register field. Make sure the field has a polygon defined.');
    }
}
