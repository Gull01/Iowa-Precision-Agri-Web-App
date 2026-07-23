/**
 * Iowa Local Data Layers
 * Displays locally downloaded data without internet connection
 * Includes LULC, climate, vegetation, and soil data for Iowa
 */

let iowaLocalLayers = {};
let iowaLayerControl = null;

/**
 * Initialize Iowa local data layers
 * @param {L.Map} map - Leaflet map instance
 */
async function initializeIowaLocalLayers(map) {
    console.log('🌾 Loading Iowa local data layers...');
    
    try {
        // Load Iowa boundary first
        const boundaryResponse = await fetch('/api/local-data/boundary');
        const boundaryData = await boundaryResponse.json();
        
        // Add Iowa state boundary as a permanent layer (no popup, not in legend)
        const iowaBoundary = L.geoJSON(boundaryData, {
            style: {
                color: '#ff0000',
                weight: 3,
                fillOpacity: 0,
                dashArray: '10, 5',
                interactive: false  // No interactions, just visual boundary
            }
        }).addTo(map);
        iowaBoundary.bringToFront();
        
        // Fetch available datasets
        const response = await fetch('/api/local-data/datasets');
        const data = await response.json();
        
        console.log(`📊 Found ${data.total_datasets} local datasets`);
        
        // Get Iowa bounds for layer restrictions
        const bounds = L.geoJSON(boundaryData).getBounds();
        
        console.log('🗺️ Iowa bounds:', bounds);
        
        // Group layers by category
        const layerGroups = {
            'Land Use / Land Cover': [],
            'Vegetation Indices': [],
            'Climate Data': [],
            'Soil Data': []
        };
        
        // Create tile layers for each dataset
        data.datasets.forEach(dataset => {
            if (!dataset.available) {
                console.warn(`⚠️ Dataset not available: ${dataset.name}`);
                return;
            }
            
            const tileUrl = dataset.tile_url.replace('{z}', '{z}').replace('{x}', '{x}').replace('{y}', '{y}');
            
            const layer = L.tileLayer(tileUrl, {
                maxZoom: 18,
                minZoom: 7,
                attribution: `Local Data: ${dataset.name}`,
                opacity: 0.7,
                bounds: bounds,  // Use GeoJSON bounds
                maxNativeZoom: 15,
                tileSize: 256,
                noWrap: true,
                zIndex: 1000  // Always on top of basemaps
            });
            
            // Store layer reference
            iowaLocalLayers[dataset.id] = {
                layer: layer,
                info: dataset
            };
            
            // Add to appropriate category
            let categoryName;
            switch (dataset.category) {
                case 'LULC':
                    categoryName = 'Land Use / Land Cover';
                    break;
                case 'Vegetation':
                    categoryName = 'Vegetation Indices';
                    break;
                case 'Climate':
                    categoryName = 'Climate Data';
                    break;
                case 'Soil':
                    categoryName = 'Soil Data';
                    break;
                default:
                    // Skip unknown categories
                    return;
            }
            
            layerGroups[categoryName].push({
                name: dataset.name,
                layer: layer,
                id: dataset.id
            });
        });
        
        // Create layer control
        createIowaLayerControl(map, layerGroups);
        
        // Keep Iowa layers on top when basemap changes
        map.on('baselayerchange', function() {
            // Bring all active Iowa layers to front
            Object.values(iowaLocalLayers).forEach(layerObj => {
                if (map.hasLayer(layerObj.layer)) {
                    layerObj.layer.bringToFront();
                }
            });
            // Keep boundary on top
            iowaBoundary.bringToFront();
        });
        
        // Add Iowa boundary indicator - pass the Leaflet bounds object
        addIowaBoundaryIndicator(map, bounds);
        
        // Add click handler for data values
        addIowaDataClickHandler(map);
        
        console.log('✅ Iowa local data layers loaded successfully');
        console.log('📍 Click handler attached - click on map to see data');
        console.log('🗺️ Available layers:', Object.keys(iowaLocalLayers));
        
        return {
            layers: iowaLocalLayers,
            control: iowaLayerControl,
            bounds: bounds
        };
        
    } catch (error) {
        console.error('❌ Error loading Iowa local data:', error);
        return null;
    }
}

/**
 * Create custom layer control for Iowa data
 */
function createIowaLayerControl(map, layerGroups) {
    const control = L.control({ position: 'topright' });
    
    control.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'iowa-layer-control leaflet-bar');
        
        let html = `
            <div class="iowa-control-header">
                <h3>Datasets</h3>
            </div>
            <div class="iowa-control-content">
        `;
        
        // Add layer groups
        Object.entries(layerGroups).forEach(([groupName, layers]) => {
            if (layers.length > 0) {
                html += `
                    <div class="iowa-layer-group">
                        <div class="iowa-group-header">${groupName}</div>
                `;
                
                layers.forEach(layerInfo => {
                    html += `
                        <div class="iowa-layer-item">
                            <label>
                                <input type="checkbox" 
                                       data-layer-id="${layerInfo.id}"
                                       class="iowa-layer-toggle">
                                <span>${layerInfo.name}</span>
                            </label>
                            <button class="iowa-info-btn" 
                                    data-layer-id="${layerInfo.id}"
                                    title="Layer information">ℹ️</button>
                        </div>
                    `;
                });
                
                html += `</div>`;
            }
        });
        
        html += `
            </div>
            <div class="iowa-control-footer">
                <button id="iowaZoomBtn" class="iowa-zoom-btn">📍 Zoom to Iowa</button>
                <button id="iowaStatsBtn" class="iowa-stats-btn">📊 View Statistics</button>
            </div>
        `;
        
        div.innerHTML = html;
        
        // Prevent map interactions when using control
        L.DomEvent.disableClickPropagation(div);
        L.DomEvent.disableScrollPropagation(div);
        
        // Add event listeners after adding to DOM
        setTimeout(() => {
            // Layer toggle checkboxes
            div.querySelectorAll('.iowa-layer-toggle').forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const layerId = this.dataset.layerId;
                    const layerObj = iowaLocalLayers[layerId];
                    
                    if (this.checked) {
                        map.addLayer(layerObj.layer);
                        console.log(`✅ Enabled layer: ${layerObj.info.name}`);
                    } else {
                        map.removeLayer(layerObj.layer);
                        console.log(`❌ Disabled layer: ${layerObj.info.name}`);
                    }
                });
            });
            
            // Info buttons
            div.querySelectorAll('.iowa-info-btn').forEach(btn => {
                btn.addEventListener('click', async function() {
                    const layerId = this.dataset.layerId;
                    await showLayerInfo(layerId);
                });
            });
            
            // Zoom to Iowa button
            const zoomBtn = div.querySelector('#iowaZoomBtn');
            if (zoomBtn) {
                zoomBtn.addEventListener('click', async function() {
                    const response = await fetch('/api/local-data/iowa-bounds');
                    const bounds = await response.json();
                    map.fitBounds([
                        [bounds.bounds.south, bounds.bounds.west],
                        [bounds.bounds.north, bounds.bounds.east]
                    ]);
                });
            }
            
            // Statistics button
            const statsBtn = div.querySelector('#iowaStatsBtn');
            if (statsBtn) {
                statsBtn.addEventListener('click', function() {
                    showIowaDataStatistics();
                });
            }
        }, 100);
        
        return div;
    };
    
    iowaLayerControl = control;
    control.addTo(map);
}

/**
 * Show layer information modal
 */
async function showLayerInfo(layerId) {
    try {
        const response = await fetch(`/api/local-data/info/${layerId}`);
        const info = await response.json();
        
        const modal = document.createElement('div');
        modal.className = 'iowa-info-modal';
        modal.innerHTML = `
            <div class="iowa-modal-content">
                <div class="iowa-modal-header">
                    <h2>${info.name}</h2>
                    <button class="iowa-modal-close">&times;</button>
                </div>
                <div class="iowa-modal-body">
                    <p><strong>Description:</strong> ${info.description}</p>
                    <p><strong>Category:</strong> ${info.category}</p>
                    <p><strong>Dimensions:</strong> ${info.width} × ${info.height} pixels</p>
                    <p><strong>Bands:</strong> ${info.bands}</p>
                    <p><strong>CRS:</strong> ${info.crs}</p>
                    ${info.statistics ? `
                        <div class="iowa-stats-box">
                            <h3>Statistics</h3>
                            <ul>
                                <li>Min: ${info.statistics.min.toFixed(2)}</li>
                                <li>Max: ${info.statistics.max.toFixed(2)}</li>
                                <li>Mean: ${info.statistics.mean.toFixed(2)}</li>
                                <li>Std Dev: ${info.statistics.std.toFixed(2)}</li>
                            </ul>
                        </div>
                    ` : ''}
                    <div class="iowa-bounds-box">
                        <h3>Geographic Bounds</h3>
                        <ul>
                            <li>North: ${info.bounds.north.toFixed(4)}°</li>
                            <li>South: ${info.bounds.south.toFixed(4)}°</li>
                            <li>East: ${info.bounds.east.toFixed(4)}°</li>
                            <li>West: ${info.bounds.west.toFixed(4)}°</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close button
        modal.querySelector('.iowa-modal-close').onclick = function() {
            document.body.removeChild(modal);
        };
        
        // Click outside to close
        modal.onclick = function(e) {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        };
        
    } catch (error) {
        alert('Error loading layer information: ' + error.message);
    }
}

/**
 * Add click handler to show data values
 */
function addIowaDataClickHandler(map) {
    console.log('🔧 Setting up Iowa data click handler...');
    
    map.on('click', async function(e) {
        console.log('🖱️ Map clicked at:', e.latlng);
        
        // Get active Iowa layers
        const activeLayers = Object.entries(iowaLocalLayers)
            .filter(([id, obj]) => map.hasLayer(obj.layer))
            .map(([id, obj]) => id);
        
        console.log('📊 Active Iowa layers:', activeLayers);
        console.log('🗺️ All Iowa layers:', Object.keys(iowaLocalLayers));
        
        if (activeLayers.length === 0) {
            console.log('⚠️ No active Iowa layers - enable a layer from the legend first');
            
            // Show a popup telling user to enable a layer
            L.popup()
                .setLatLng(e.latlng)
                .setContent(`
                    <div style="padding: 15px; text-align: center;">
                        <h4 style="margin: 0 0 10px 0; color: #f57c00;">⚠️ No Active Layers</h4>
                        <p style="margin: 0; color: #666;">
                            Enable a data layer from the<br>
                            <strong>Iowa Local Data</strong> panel<br>
                            to see values here.
                        </p>
                    </div>
                `)
                .openOn(map);
            return;
        }
        
        const { lat, lng } = e.latlng;
        
        // Show loading popup immediately
        const loadingPopup = L.popup()
            .setLatLng(e.latlng)
            .setContent('<div style="padding: 10px; text-align: center;">⏳ Loading data...</div>')
            .openOn(map);
        
        // Create popup content with better styling
        let popupContent = `<div class="iowa-data-popup" style="min-width: 280px;">
            <h4 style="margin: 0 0 12px 0; color: #2e7d32; border-bottom: 2px solid #4caf50; padding-bottom: 8px;">
                📍 Iowa Local Data
            </h4>
            <p style="margin: 4px 0 10px 0; color: #666; font-size: 12px;">
                <strong>Coordinates:</strong><br>
                Lat: ${lat.toFixed(5)}° N<br>
                Lon: ${lng.toFixed(5)}° W
            </p>
            <hr style="margin: 10px 0; border: none; border-top: 1px solid #ddd;">
        `;
        
        let hasData = false;
        
        // Fetch values for each active layer
        for (const layerId of activeLayers) {
            try {
                const response = await fetch(
                    `/api/local-data/point-value/${layerId}?lat=${lat}&lon=${lng}`
                );
                const data = await response.json();
                
                const layerInfo = iowaLocalLayers[layerId].info;
                const layerName = layerInfo.name;
                const shortName = layerName.replace('Iowa ', '').replace('Landsat ', '').replace('GridMET ', '').replace('SMAP ', '');
                
                // Use display_value for categorical data (CDL/NLCD), numeric for others
                let displayText;
                let valueColor = '#333';
                
                if (data.class_name) {
                    // Categorical data (crop type or land cover)
                    displayText = `<strong style="color: #1976d2;">${data.class_name}</strong>`;
                } else if (data.display_value !== null && data.display_value !== undefined) {
                    // Numeric data with color coding
                    const value = parseFloat(data.display_value);
                    
                    // Color code based on layer type
                    if (layerId.includes('ndvi')) {
                        if (value > 0.6) valueColor = '#2e7d32'; // High NDVI - green
                        else if (value > 0.3) valueColor = '#f9a825'; // Medium - yellow
                        else valueColor = '#d32f2f'; // Low - red
                    } else if (layerId.includes('rainfall')) {
                        valueColor = '#1976d2'; // Blue for water
                    } else if (layerId.includes('tmax')) {
                        if (value > 30) valueColor = '#d32f2f'; // Hot - red
                        else if (value > 20) valueColor = '#f9a825'; // Warm - orange
                        else valueColor = '#1976d2'; // Cool - blue
                    } else if (layerId.includes('soil_moisture')) {
                        valueColor = '#795548'; // Brown for soil
                    }
                    
                    displayText = `<strong style="color: ${valueColor};">${value.toFixed(2)} ${data.unit || ''}</strong>`;
                } else {
                    displayText = '<em style="color: #999;">No data at this location</em>';
                }
                
                hasData = true;
                
                popupContent += `
                    <div style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 6px; border-left: 3px solid #4caf50;">
                        <div style="font-size: 12px; color: #666; margin-bottom: 4px;">
                            ${shortName}
                        </div>
                        <div style="font-size: 14px;">
                            ${displayText}
                        </div>
                    </div>
                `;
            } catch (error) {
                console.error(`Error fetching value for ${layerId}:`, error);
                popupContent += `
                    <div style="margin: 10px 0; padding: 10px; background: #ffebee; border-radius: 6px; border-left: 3px solid #f44336;">
                        <div style="font-size: 12px; color: #c62828;">
                            ❌ Error loading ${layerId}
                        </div>
                    </div>
                `;
            }
        }
        
        if (!hasData) {
            popupContent += `
                <div style="margin: 10px 0; padding: 15px; background: #fff3cd; border-radius: 6px; text-align: center; color: #856404;">
                    ⚠️ No data available at this location
                </div>
            `;
        }
        
        popupContent += '</div>';
        
        // Update popup with actual data
        L.popup()
            .setLatLng(e.latlng)
            .setContent(popupContent)
            .openOn(map);
    });
}

/**
 * Add Iowa boundary indicator
 */
function addIowaBoundaryIndicator(map, bounds) {
    // bounds is already a Leaflet LatLngBounds object
    const rectangle = L.rectangle(bounds, {
        color: '#FFC107',
        weight: 2,
        fillOpacity: 0,
        dashArray: '10, 5',
        interactive: false
    });
    
    rectangle.bindTooltip('Iowa State Boundary', { 
        permanent: false, 
        direction: 'center' 
    });
    
    rectangle.addTo(map);
    
    // Restrict map view to Iowa region with padding
    const sw = bounds.getSouthWest();
    const ne = bounds.getNorthEast();
    
    map.setMaxBounds([
        [sw.lat - 0.5, sw.lng - 0.5],
        [ne.lat + 0.5, ne.lng + 0.5]
    ]);
}

/**
 * Show Iowa data statistics dashboard
 */
async function showIowaDataStatistics() {
    const modal = document.createElement('div');
    modal.className = 'iowa-info-modal';
    modal.innerHTML = `
        <div class="iowa-modal-content iowa-modal-wide">
            <div class="iowa-modal-header">
                <h2>📊 Iowa Local Data Statistics</h2>
                <button class="iowa-modal-close">&times;</button>
            </div>
            <div class="iowa-modal-body">
                <div class="loading">Loading statistics...</div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close handlers
    modal.querySelector('.iowa-modal-close').onclick = function() {
        document.body.removeChild(modal);
    };
    modal.onclick = function(e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    };
    
    // Load statistics for all datasets
    const modalBody = modal.querySelector('.iowa-modal-body');
    let statsHtml = '<div class="iowa-stats-grid">';
    
    for (const [layerId, layerObj] of Object.entries(iowaLocalLayers)) {
        try {
            const response = await fetch(`/api/local-data/stats/${layerId}`);
            const stats = await response.json();
            
            statsHtml += `
                <div class="iowa-stat-card">
                    <h3>${layerObj.info.name}</h3>
                    <div class="stat-row">
                        <span>Min:</span>
                        <span><strong>${stats.min.toFixed(2)} ${stats.unit}</strong></span>
                    </div>
                    <div class="stat-row">
                        <span>Max:</span>
                        <span><strong>${stats.max.toFixed(2)} ${stats.unit}</strong></span>
                    </div>
                    <div class="stat-row">
                        <span>Mean:</span>
                        <span><strong>${stats.mean.toFixed(2)} ${stats.unit}</strong></span>
                    </div>
                    <div class="stat-row">
                        <span>Std Dev:</span>
                        <span><strong>${stats.std.toFixed(2)}</strong></span>
                    </div>
                    <div class="stat-row">
                        <span>Data Points:</span>
                        <span><strong>${stats.count.toLocaleString()}</strong></span>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error(`Error loading stats for ${layerId}:`, error);
        }
    }
    
    statsHtml += '</div>';
    modalBody.innerHTML = statsHtml;
}

/**
 * Create Iowa layers panel in sidebar
 */
function createIowaSidebarPanel(map, layerGroups) {
    const panel = document.getElementById('iowaLayersPanel');
    if (!panel) {
        console.warn('⚠️ Iowa layers panel container not found in sidebar');
        return;
    }
    
    let html = '';
    
    // Add layer groups
    Object.entries(layerGroups).forEach(([groupName, layers]) => {
        if (layers.length > 0) {
            html += `
                <div class="layer-group" style="margin-bottom: 15px;">
                    <h4 style="font-size: 13px; font-weight: 600; color: #2c5530; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                        ${getGroupIcon(groupName)} ${groupName}
                    </h4>
                    <div class="layer-list">
            `;
            
            layers.forEach(layerInfo => {
                const checked = layerInfo.id === 'iowa_cdl' ? 'checked' : '';  // CDL on by default
                html += `
                    <label class="layer-checkbox" style="display: flex; align-items: center; padding: 6px 8px; margin: 2px 0; border-radius: 4px; cursor: pointer; transition: background 0.2s; font-size: 13px;">
                        <input 
                            type="checkbox" 
                            data-layer-id="${layerInfo.id}" 
                            ${checked}
                            style="margin-right: 8px; cursor: pointer;"
                            onchange="toggleIowaLayer('${layerInfo.id}', this.checked)">
                        <span style="color: #333;">${layerInfo.name}</span>
                    </label>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
    });
    
    // Add layer info button
    html += `
        <button class="btn btn-secondary" onclick="showIowaDatasetInfo()" style="width: 100%; margin-top: 10px;">
            ℹ️ Dataset Information
        </button>
    `;
    
    panel.innerHTML = html;
    
    // Add hover effect styles
    const style = document.createElement('style');
    style.textContent = `
        .layer-checkbox:hover {
            background: #f0f2f5;
        }
        .layer-checkbox input[type="checkbox"] {
            width: 16px;
            height: 16px;
        }
    `;
    document.head.appendChild(style);
    
    console.log('✅ Iowa layers sidebar panel created');
}

/**
 * Get icon for layer group
 */
function getGroupIcon(groupName) {
    const icons = {
        'Land Use / Land Cover': '🌍',
        'Vegetation Indices': '🌱',
        'Climate Data': '🌤️',
        'Soil Data': '🏔️'
    };
    return icons[groupName] || '📊';
}

/**
 * Toggle Iowa layer on/off
 */
function toggleIowaLayer(layerId, show) {
    const layerData = iowaLocalLayers[layerId];
    if (!layerData) {
        console.warn(`⚠️ Layer not found: ${layerId}`);
        return;
    }
    
    const map = window.map;  // Assumes global map variable
    if (!map) {
        console.error('❌ Map not found');
        return;
    }
    
    if (show) {
        layerData.layer.addTo(map);
        console.log(`✅ Layer added: ${layerId}`);
    } else {
        map.removeLayer(layerData.layer);
        console.log(`➖ Layer removed: ${layerId}`);
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.initializeIowaLocalLayers = initializeIowaLocalLayers;
    window.iowaLocalLayers = iowaLocalLayers;
    window.toggleIowaLayer = toggleIowaLayer;
}
