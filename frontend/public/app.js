// Frontend JavaScript for Semiconductor Yield Prediction System

const API_BASE = '/api';

// DOM Elements
const datasetSelect = document.getElementById('datasetSelect');
const analyzeBtn = document.getElementById('analyzeBtn');
const analyzeText = document.getElementById('analyzeText');
const analyzeLoading = document.getElementById('analyzeLoading');
const resultsSection = document.getElementById('resultsSection');
const downloadPdfBtn = document.getElementById('downloadPdfBtn');

// Charts
let yieldChart = null;
let parameterChart = null;
let currentAnalysisData = null;
let availableDatasets = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  analyzeBtn.addEventListener('click', handleAnalyze);
  downloadPdfBtn.addEventListener('click', handleDownloadPdf);
  
  // Dataset management
  document.getElementById('uploadDatasetBtn').addEventListener('click', handleUploadDataset);
  document.getElementById('refreshDatasetsBtn').addEventListener('click', loadDatasets);
  
  // Dataset selection change
  datasetSelect.addEventListener('change', handleDatasetSelect);
  
  // Load datasets on page load
  loadDatasets();
});

// Handle dataset selection
async function handleDatasetSelect() {
  const selectedId = datasetSelect.value;
  if (!selectedId) {
    return;
  }
  
  try {
    // Load dataset data
    const response = await fetch(`${API_BASE}/datasets/${selectedId}`);
    const datasetData = await response.json();
    
    // Convert dataset to wafer data format
    const convertResponse = await fetch(`${API_BASE}/datasets/${selectedId}/convert`, {
      method: 'POST'
    });
    
    if (convertResponse.ok) {
      const convertedData = await convertResponse.json();
      
      // Populate form fields with converted data
      if (convertedData.wafer_data) {
        document.getElementById('waferId').value = convertedData.wafer_data.wafer_id || 'WAFER_001';
        document.getElementById('totalDies').value = convertedData.wafer_data.wafer_map?.total_dies || 500;
        document.getElementById('goodDies').value = convertedData.wafer_data.wafer_map?.good_dies || 465;
        document.getElementById('defectDensity').value = convertedData.wafer_data.wafer_map?.defect_density || 0.07;
        document.getElementById('thicknessMean').value = convertedData.wafer_data.metrology_data?.thickness?.mean || 1.2;
        document.getElementById('thicknessStd').value = convertedData.wafer_data.metrology_data?.thickness?.std || 0.05;
        document.getElementById('cdTarget').value = convertedData.wafer_data.metrology_data?.critical_dimensions?.target || 0.1;
        document.getElementById('cdActual').value = convertedData.wafer_data.metrology_data?.critical_dimensions?.actual || 0.102;
      }
      
      if (convertedData.current_parameters) {
        document.getElementById('temperature').value = convertedData.current_parameters.temperature || 198.5;
        document.getElementById('etchTime').value = convertedData.current_parameters.etch_time || 46.2;
        document.getElementById('exposureDose').value = convertedData.current_parameters.exposure_dose || 51.5;
      }
    }
  } catch (error) {
    console.error('Error loading dataset:', error);
    // If conversion fails, just use default values
  }
}

// Handle analyze button - Show results side by side
async function handleAnalyze() {
  analyzeBtn.disabled = true;
  analyzeText.style.display = 'none';
  analyzeLoading.style.display = 'inline';
  
  // Show placeholder while analyzing
  document.getElementById('resultsPlaceholder').style.display = 'block';
  document.getElementById('resultsContent').style.display = 'none';

  try {
    const waferData = {
      wafer_id: document.getElementById('waferId').value,
      wafer_map: {
        total_dies: parseInt(document.getElementById('totalDies').value),
        good_dies: parseInt(document.getElementById('goodDies').value),
        defect_density: parseFloat(document.getElementById('defectDensity').value)
      },
      metrology_data: {
        thickness: {
          mean: parseFloat(document.getElementById('thicknessMean').value),
          std: parseFloat(document.getElementById('thicknessStd').value)
        },
        critical_dimensions: {
          target: parseFloat(document.getElementById('cdTarget').value),
          actual: parseFloat(document.getElementById('cdActual').value)
        }
      },
      eda_logs: []
    };

    const currentParameters = {
      temperature: parseFloat(document.getElementById('temperature').value),
      etch_time: parseFloat(document.getElementById('etchTime').value),
      exposure_dose: parseFloat(document.getElementById('exposureDose').value)
    };

    // Get analysis results
    const response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        wafer_data: waferData,
        current_parameters: currentParameters
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    currentAnalysisData = { waferData, currentParameters, result };
    
    // Display results in the right column
    displayResults(result);
    
    // Show results content and hide placeholder
    document.getElementById('resultsPlaceholder').style.display = 'none';
    document.getElementById('resultsContent').style.display = 'block';
  } catch (error) {
    console.error('Analysis error:', error);
    alert('Analysis failed: ' + error.message);
  } finally {
    analyzeBtn.disabled = false;
    analyzeText.style.display = 'inline';
    analyzeLoading.style.display = 'none';
  }
}

// Handle PDF download
async function handleDownloadPdf() {
  if (!currentAnalysisData) {
    alert('Please run analysis first!');
    return;
  }

  downloadPdfBtn.disabled = true;
  downloadPdfBtn.textContent = '⏳ Generating PDF...';

  try {
    const response = await fetch(`${API_BASE}/generate-report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        wafer_data: currentAnalysisData.waferData,
        current_parameters: currentAnalysisData.currentParameters
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Get PDF blob and download it
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `yield_report_${currentAnalysisData.waferData.wafer_id}_${new Date().toISOString().slice(0, 10)}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    alert('✅ PDF Report downloaded successfully!');
  } catch (error) {
    console.error('PDF generation error:', error);
    alert('PDF generation failed: ' + error.message);
  } finally {
    downloadPdfBtn.disabled = false;
    downloadPdfBtn.textContent = '📥 Download PDF Report';
  }
}

// Display results
function displayResults(result) {
  // Update metrics
  document.getElementById('predictedYield').textContent = 
    result.prediction.predicted_yield.toFixed(2) + '%';
  document.getElementById('confidence').textContent = 
    (result.prediction.confidence * 100).toFixed(0) + '%';
  document.getElementById('optimizedYield').textContent = 
    result.optimization.optimized_yield.toFixed(2) + '%';
  document.getElementById('improvement').textContent = 
    '+' + result.optimization.improvement_percentage.toFixed(2) + '%';

  // Update optimized parameters
  document.getElementById('optTemperature').textContent = 
    result.optimization.recommended_parameters.temperature.toFixed(2) + '°C';
  document.getElementById('optEtchTime').textContent = 
    result.optimization.recommended_parameters.etch_time.toFixed(2) + 's';
  document.getElementById('optExposureDose').textContent = 
    result.optimization.recommended_parameters.exposure_dose.toFixed(2) + ' mJ/cm²';

  // Create yield chart
  createYieldChart(result);

  // Create parameter chart
  createParameterChart(result);

  // Display recommendations
  displayRecommendations(result.recommendations);

  // Show results section
  resultsSection.style.display = 'block';
}

// Create yield comparison chart
function createYieldChart(result) {
  const ctx = document.getElementById('yieldChart');
  if (yieldChart) {
    yieldChart.destroy();
  }

  yieldChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Current Yield', 'Optimized Yield'],
      datasets: [{
        label: 'Yield (%)',
        data: [
          result.optimization.current_yield,
          result.optimization.optimized_yield
        ],
        backgroundColor: ['#cbd5e0', '#667eea'],
        borderColor: ['#a0aec0', '#5568d3'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function(value) {
              return value + '%';
            }
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return 'Yield: ' + context.parsed.y.toFixed(2) + '%';
            }
          }
        }
      }
    }
  });
}

// Create parameter comparison chart
function createParameterChart(result) {
  const ctx = document.getElementById('parameterChart');
  if (parameterChart) {
    parameterChart.destroy();
  }

  const currentParams = result.current_parameters || {
    temperature: parseFloat(document.getElementById('temperature').value),
    etch_time: parseFloat(document.getElementById('etchTime').value),
    exposure_dose: parseFloat(document.getElementById('exposureDose').value)
  };

  parameterChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Temperature (°C)', 'Etch Time (s)', 'Exposure Dose (mJ/cm²)'],
      datasets: [
        {
          label: 'Current',
          data: [
            currentParams.temperature,
            currentParams.etch_time,
            currentParams.exposure_dose
          ],
          backgroundColor: '#cbd5e0',
          borderColor: '#a0aec0',
          borderWidth: 2
        },
        {
          label: 'Optimized',
          data: [
            result.optimization.recommended_parameters.temperature,
            result.optimization.recommended_parameters.etch_time,
            result.optimization.recommended_parameters.exposure_dose
          ],
          backgroundColor: '#667eea',
          borderColor: '#5568d3',
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      }
    }
  });
}

// Display recommendations
function displayRecommendations(recommendations) {
  const container = document.getElementById('recommendationsList');
  container.innerHTML = '';

  if (!recommendations || recommendations.length === 0) {
    container.innerHTML = '<p class="no-recommendations">No specific recommendations at this time.</p>';
    return;
  }

  recommendations.forEach(rec => {
    const item = document.createElement('div');
    item.className = 'recommendation-item';

    const icon = rec.action === 'reduce' ? '🔽' : rec.action === 'increase' ? '🔼' : '⚙️';
    const actionText = rec.action.charAt(0).toUpperCase() + rec.action.slice(1);
    const paramText = rec.parameter.replace('_', ' ');

    item.innerHTML = `
      <div class="recommendation-title">
        ${icon} ${actionText} ${paramText}
      </div>
      <div class="recommendation-text">
        ${rec.description}
      </div>
      <div class="recommendation-metrics">
        <span class="metric-badge">Current: ${rec.current_value.toFixed(2)}</span>
        <span class="metric-badge">Recommended: ${rec.recommended_value.toFixed(2)}</span>
        <span class="metric-badge improvement">Improvement: +${rec.improvement.toFixed(2)}%</span>
      </div>
    `;

    container.appendChild(item);
  });
}

// Dataset Management Functions

// Load list of datasets
async function loadDatasets() {
  try {
    const response = await fetch(`${API_BASE}/datasets`);
    const data = await response.json();
    availableDatasets = data.datasets || [];
    displayDatasets(availableDatasets);
    updateDatasetSelect(availableDatasets);
  } catch (error) {
    console.error('Error loading datasets:', error);
    document.getElementById('datasetsList').innerHTML = 
      '<p style="color: #e53e3e;">Error loading datasets: ' + error.message + '</p>';
  }
}

// Update dataset select dropdown
function updateDatasetSelect(datasets) {
  const select = datasetSelect;
  const currentValue = select.value;
  
  // Clear existing options except the first one
  select.innerHTML = '<option value="">-- Select a dataset to analyze --</option>';
  
  // Add dataset options
  datasets.forEach(dataset => {
    const option = document.createElement('option');
    option.value = dataset.id;
    option.textContent = `${dataset.name || dataset.id} (${dataset.rows} rows)`;
    select.appendChild(option);
  });
  
  // Restore previous selection if it still exists
  if (currentValue && datasets.find(d => d.id === currentValue)) {
    select.value = currentValue;
  }
}

// Display datasets list
function displayDatasets(datasets) {
  const container = document.getElementById('datasetsList');
  
  if (!datasets || datasets.length === 0) {
    container.innerHTML = '<p style="color: #718096; font-style: italic;">No datasets available. Upload or download one to get started.</p>';
    return;
  }
  
  container.innerHTML = '';
  
  datasets.forEach(dataset => {
    const item = document.createElement('div');
    item.className = 'dataset-item';
    item.style.cssText = 'background: #f7fafc; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #667eea;';
    
    const sourceIcon = dataset.source === 'huggingface' ? '🤗' : '📁';
    const date = dataset.downloaded_at || dataset.uploaded_at || 'Unknown';
    
    item.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: start;">
        <div style="flex: 1;">
          <div style="font-weight: 600; color: #2d3748; margin-bottom: 5px;">
            ${sourceIcon} ${dataset.name || dataset.id}
          </div>
          <div style="font-size: 12px; color: #718096; margin-bottom: 5px;">
            Rows: ${dataset.rows} | Columns: ${dataset.columns?.length || 0}
          </div>
          <div style="font-size: 11px; color: #a0aec0;">
            ${new Date(date).toLocaleString()}
          </div>
        </div>
        <button class="delete-dataset-btn" data-id="${dataset.id}" style="background: #e53e3e; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px;">
          🗑️ Delete
        </button>
      </div>
    `;
    
    // Add delete handler
    const deleteBtn = item.querySelector('.delete-dataset-btn');
    deleteBtn.addEventListener('click', () => handleDeleteDataset(dataset.id));
    
    container.appendChild(item);
  });
}

// Upload local dataset
async function handleUploadDataset() {
  const fileInput = document.getElementById('datasetFile');
  const datasetName = document.getElementById('uploadDatasetName').value.trim();
  
  if (!fileInput.files || fileInput.files.length === 0) {
    alert('Please select a file');
    return;
  }
  
  if (!fileInput.files[0]) {
    alert('Please select a file to upload');
    return;
  }
  
  const file = fileInput.files[0];
  
  // Validate file type before upload
  const fileName = file.name.toLowerCase();
  if (!fileName.endsWith('.json') && !fileName.endsWith('.csv')) {
    alert('❌ Invalid file type!\n\nPlease select a JSON (.json) or CSV (.csv) file.\n\nNote: PDF files are output reports, not input datasets.');
    return;
  }
  
  const btn = document.getElementById('uploadDatasetBtn');
  const originalText = btn.textContent;
  
  btn.disabled = true;
  btn.textContent = '⏳ Uploading...';
  
  try {
    const formData = new FormData();
    formData.append('file', file);
    // Always send dataset_name field (even if empty) - backend will auto-generate from filename if empty
    formData.append('dataset_name', datasetName && datasetName.trim() !== '' ? datasetName.trim() : '');
    
    const response = await fetch(`${API_BASE}/datasets/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }
    
    const result = await response.json();
    alert(`✅ ${result.message}\n\nDataset ID: ${result.dataset_id}\nRows: ${result.rows}`);
    
    // Clear form
    document.getElementById('uploadDatasetName').value = '';
    fileInput.value = '';
    
    // Refresh list and select the new dataset
    await loadDatasets();
    
    // Auto-select the newly uploaded dataset
    if (result.dataset_id) {
      datasetSelect.value = result.dataset_id;
      handleDatasetSelect();
    }
  } catch (error) {
    console.error('Upload error:', error);
    alert('Upload failed: ' + error.message);
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
  }
}

// Delete dataset
async function handleDeleteDataset(datasetId) {
  if (!confirm(`Are you sure you want to delete dataset ${datasetId}?`)) {
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE}/datasets/${datasetId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Delete failed');
    }
    
    alert('✅ Dataset deleted successfully');
    loadDatasets();
  } catch (error) {
    console.error('Delete error:', error);
    alert('Delete failed: ' + error.message);
  }
}

