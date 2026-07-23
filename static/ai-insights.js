/**
 * AI Insights Integration for Iowa Datasets
 * Provides intelligent analysis using Gemini AI and local data
 */

let aiInsightsPanel = null;
let isLoadingInsights = false;

/**
 * Initialize AI Insights functionality
 */
function initializeAIInsights(map) {
    console.log('🤖 Initializing AI Insights...');
    
    // Create AI insights panel
    createAIInsightsPanel();
    
    // Add AI insights button to map
    addAIInsightsButton(map);
    
    console.log('✅ AI Insights initialized');
}

/**
 * Create AI Insights Panel UI
 */
function createAIInsightsPanel() {
    const panel = document.createElement('div');
    panel.id = 'ai-insights-panel';
    panel.className = 'ai-insights-panel hidden';
    panel.innerHTML = `
        <div class="ai-panel-header">
            <h3>🤖 AI Insights</h3>
            <button class="close-btn" onclick="closeAIPanel()">×</button>
        </div>
        <div class="ai-panel-content">
            <div class="location-info">
                <p class="info-text">Click on the map to get AI-powered insights for any location in Iowa</p>
            </div>
            <div id="ai-insights-content" class="insights-content">
                <!-- Insights will be loaded here -->
            </div>
        </div>
    `;
    
    document.body.appendChild(panel);
    aiInsightsPanel = panel;
}

/**
 * Add AI Insights button to map
 */
function addAIInsightsButton(map) {
    const AIInsightsControl = L.Control.extend({
        options: {
            position: 'topright'
        },
        
        onAdd: function() {
            const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control ai-insights-control');
            container.innerHTML = `
                <a href="#" title="AI Insights" class="ai-insights-btn">
                    <span style="font-size: 16px;">🤖</span>
                </a>
            `;
            
            container.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                toggleAIPanel();
            };
            
            L.DomEvent.disableClickPropagation(container);
            
            return container;
        }
    });
    
    map.addControl(new AIInsightsControl());
}

/**
 * Toggle AI Panel visibility
 */
function toggleAIPanel() {
    if (aiInsightsPanel.classList.contains('hidden')) {
        aiInsightsPanel.classList.remove('hidden');
        // Show instruction if no insights yet
        const content = document.getElementById('ai-insights-content');
        if (!content.hasChildNodes() || content.children.length === 0) {
            showWelcomeMessage();
        }
    } else {
        aiInsightsPanel.classList.add('hidden');
    }
}

/**
 * Close AI Panel
 */
function closeAIPanel() {
    aiInsightsPanel.classList.add('hidden');
}

/**
 * Show welcome message
 */
function showWelcomeMessage() {
    const content = document.getElementById('ai-insights-content');
    content.innerHTML = `
        <div class="welcome-message">
            <h4>Welcome to AI Insights</h4>
            <p>Get intelligent analysis powered by Google Gemini AI based on your Iowa datasets:</p>
            <ul>
                <li>📊 Crop recommendations based on soil and climate</li>
                <li>🌱 Field health analysis using NDVI data</li>
                <li>🌦️ Weather impact predictions</li>
                <li>💧 Soil moisture and irrigation advice</li>
                <li>🎯 Location-specific insights</li>
            </ul>
            <p class="action-text">Click anywhere on the Iowa map to start!</p>
        </div>
    `;
}

/**
 * Get AI insights for a location
 */
async function getAIInsights(lat, lng, activeDatasets) {
    if (isLoadingInsights) {
        console.log('Already loading insights...');
        return;
    }
    
    isLoadingInsights = true;
    
    // Show loading state
    showLoadingInsights(lat, lng);
    
    try {
        // Gather data from all active layers
        const locationData = await gatherLocationData(lat, lng, activeDatasets);
        
        // Send to AI for analysis
        const insights = await requestAIAnalysis(lat, lng, locationData);
        
        // Display results
        displayAIInsights(insights, lat, lng, locationData);
        
    } catch (error) {
        console.error('Error getting AI insights:', error);
        showErrorMessage(error.message);
    } finally {
        isLoadingInsights = false;
    }
}

/**
 * Show loading state
 */
function showLoadingInsights(lat, lng) {
    // Open panel if closed
    if (aiInsightsPanel.classList.contains('hidden')) {
        aiInsightsPanel.classList.remove('hidden');
    }
    
    const content = document.getElementById('ai-insights-content');
    content.innerHTML = `
        <div class="loading-insights">
            <div class="spinner"></div>
            <p>Analyzing location data...</p>
            <p class="coords">📍 ${lat.toFixed(4)}°N, ${Math.abs(lng).toFixed(4)}°W</p>
            <p class="status">Gathering dataset information...</p>
        </div>
    `;
}

/**
 * Gather all available data for the location
 */
async function gatherLocationData(lat, lng, activeDatasets) {
    const data = {
        location: { lat, lng },
        datasets: {}
    };
    
    // Update status
    updateLoadingStatus('Fetching data from local datasets...');
    
    try {
        // Fetch data from each dataset individually
        const datasetNames = [
            { key: 'Iowa CDL 2023', layer: 'iowa_cdl' },
            { key: 'Iowa NLCD 2021', layer: 'iowa_nlcd' },
            { key: 'Iowa NDVI', layer: 'iowa_ndvi' },
            { key: 'Iowa GridMET Rainfall', layer: 'iowa_rainfall' },
            { key: 'Iowa GridMET Max Temp', layer: 'iowa_tmax' },
            { key: 'Iowa SMAP Soil Moisture', layer: 'iowa_soil_moisture' },
            { key: 'Iowa Landsat ET', layer: 'iowa_et' }
        ];
        
        // Fetch all datasets in parallel
        const promises = datasetNames.map(async (dataset) => {
            try {
                const response = await fetch(`/api/local-data/point-value/${dataset.layer}?lat=${lat}&lon=${lng}`);
                if (response.ok) {
                    const result = await response.json();
                    // Use display_value for categorical data (CDL, NLCD), value for numeric
                    if (result.display_value !== null && result.display_value !== undefined) {
                        data.datasets[dataset.key] = result.display_value;
                    } else if (result.value !== null && result.value !== undefined) {
                        data.datasets[dataset.key] = result.value;
                    }
                }
            } catch (error) {
                console.error(`Error fetching ${dataset.key}:`, error);
            }
        });
        
        await Promise.all(promises);
        
    } catch (error) {
        console.error('Error fetching location data:', error);
    }
    
    return data;
}

/**
 * Request AI analysis from backend
 */
async function requestAIAnalysis(lat, lng, locationData) {
    updateLoadingStatus('Generating AI insights...');
    
    const response = await fetch('/api/ai/location-insights', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            latitude: lat,
            longitude: lng,
            data: locationData
        })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to generate insights');
    }
    
    return await response.json();
}

/**
 * Display AI insights
 */
function displayAIInsights(insights, lat, lng, locationData) {
    const content = document.getElementById('ai-insights-content');
    
    let html = `
        <div class="insights-result">
            <div class="location-header">
                <h4>📍 Location Analysis</h4>
                <p class="coords">${lat.toFixed(4)}°N, ${Math.abs(lng).toFixed(4)}°W</p>
            </div>
    `;
    
    // Show current data values
    html += `<div class="current-data">`;
    html += `<h5>Current Conditions:</h5>`;
    html += `<div class="data-grid">`;
    
    const datasets = locationData.datasets;
    
    if (datasets['Iowa CDL 2023']) {
        html += `<div class="data-item">
            <span class="data-label">🌾 Land Use:</span>
            <span class="data-value">${datasets['Iowa CDL 2023']}</span>
        </div>`;
    }
    
    if (datasets['Iowa NDVI']) {
        const ndvi = parseFloat(datasets['Iowa NDVI']);
        const health = ndvi > 0.6 ? 'Healthy' : ndvi > 0.3 ? 'Moderate' : 'Stressed';
        html += `<div class="data-item">
            <span class="data-label">🌱 Vegetation:</span>
            <span class="data-value">${datasets['Iowa NDVI']} (${health})</span>
        </div>`;
    }
    
    if (datasets['Iowa GridMET Rainfall']) {
        html += `<div class="data-item">
            <span class="data-label">🌧️ Rainfall:</span>
            <span class="data-value">${datasets['Iowa GridMET Rainfall']} mm</span>
        </div>`;
    }
    
    if (datasets['Iowa GridMET Max Temp']) {
        html += `<div class="data-item">
            <span class="data-label">🌡️ Temperature:</span>
            <span class="data-value">${datasets['Iowa GridMET Max Temp']}°C</span>
        </div>`;
    }
    
    if (datasets['Iowa SMAP Soil Moisture']) {
        html += `<div class="data-item">
            <span class="data-label">💧 Soil Moisture:</span>
            <span class="data-value">${datasets['Iowa SMAP Soil Moisture']} m³/m³</span>
        </div>`;
    }
    
    if (datasets['Iowa Landsat ET']) {
        html += `<div class="data-item">
            <span class="data-label">💨 Evapotranspiration:</span>
            <span class="data-value">${datasets['Iowa Landsat ET']} mm</span>
        </div>`;
    }
    
    html += `</div></div>`;
    
    // AI Analysis
    html += `<div class="ai-analysis">`;
    html += `<h5>🤖 AI Analysis:</h5>`;
    html += `<div class="analysis-content">${formatAIResponse(insights.recommendation || insights.analysis)}</div>`;
    html += `</div>`;
    
    // Action buttons
    html += `
        <div class="insight-actions">
            <button class="btn-secondary" onclick="exportInsights()">📄 Export Report</button>
            <button class="btn-primary" onclick="getAIInsights(${lat}, ${lng}, window.activeIowaLayers || [])">🔄 Refresh</button>
        </div>
    `;
    
    html += `</div>`;
    
    content.innerHTML = html;
}

/**
 * Format AI response text
 */
function formatAIResponse(text) {
    if (!text) return '<p>No analysis available</p>';
    
    // Split by sections (marked with **)
    let formatted = text
        // Convert **Header** to proper headers
        .replace(/\*\*([^*]+)\*\*/g, '<h6 class="insight-section">$1</h6>')
        // Convert bullet points
        .replace(/\n• /g, '<br>• ')
        // Convert line breaks
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    // Wrap in paragraph if not already
    if (!formatted.startsWith('<p>') && !formatted.startsWith('<h6>')) {
        formatted = '<p>' + formatted + '</p>';
    }
    
    // Add some spacing after section headers
    formatted = formatted.replace(/<\/h6>/g, '</h6><div class="section-content">');
    formatted = formatted.replace(/<h6/g, '</div><h6');
    
    // Clean up empty divs
    formatted = formatted.replace(/<\/div><h6/g, '<h6');
    formatted = formatted.replace(/<div class="section-content"><\/p>/g, '</p><div class="section-content">');
    
    return formatted + '</div>';
}

/**
 * Update loading status message
 */
function updateLoadingStatus(message) {
    const statusElement = document.querySelector('.loading-insights .status');
    if (statusElement) {
        statusElement.textContent = message;
    }
}

/**
 * Show error message
 */
function showErrorMessage(message) {
    const content = document.getElementById('ai-insights-content');
    content.innerHTML = `
        <div class="error-message">
            <h4>⚠️ Error</h4>
            <p>${message}</p>
            <button class="btn-primary" onclick="showWelcomeMessage()">Try Again</button>
        </div>
    `;
}

/**
 * Export insights as text report
 */
function exportInsights() {
    const content = document.querySelector('.insights-result');
    if (!content) return;
    
    const text = content.innerText;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-insights-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Add click handler to map for AI insights
 */
function attachAIClickHandler(map) {
    map.on('click', function(e) {
        // Only trigger if AI panel is open
        if (!aiInsightsPanel.classList.contains('hidden')) {
            const { lat, lng } = e.latlng;
            
            // Check if click is within Iowa bounds (approximate)
            if (lat >= 40.375 && lat <= 43.501 && lng >= -96.639 && lng <= -90.140) {
                getAIInsights(lat, lng, window.activeIowaLayers || []);
            } else {
                showErrorMessage('Please click within Iowa state boundaries');
            }
        }
    });
}

// Export functions for global use
window.initializeAIInsights = initializeAIInsights;
window.toggleAIPanel = toggleAIPanel;
window.closeAIPanel = closeAIPanel;
window.getAIInsights = getAIInsights;
window.attachAIClickHandler = attachAIClickHandler;
window.exportInsights = exportInsights;
