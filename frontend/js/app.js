const API_BASE = 'http://localhost:5000/api';

// DOM Elements
const uploadArea = document.getElementById('upload-area');
const imageInput = document.getElementById('image-input');
const analyzeBtn = document.getElementById('analyze-btn');
const uploadSection = document.getElementById('upload-section');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');

let selectedFile = null;

// Upload Area Interactions
uploadArea.addEventListener('click', () => imageInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    handleFileSelect(e.dataTransfer.files[0]);
});

imageInput.addEventListener('change', (e) => {
    handleFileSelect(e.target.files[0]);
});

function handleFileSelect(file) {
    if (!file) return;
    
    if (!file.type.match('image/(jpeg|jpg|png)')) {
        alert('Please select a JPG or PNG image');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
    }
    
    selectedFile = file;
    uploadArea.querySelector('.upload-content p').textContent = `Selected: ${file.name}`;
    analyzeBtn.disabled = false;
}

analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('image', selectedFile);
    
    // Show loading
    uploadSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');
    
    try {
        const response = await fetch(`${API_BASE}/scan`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const data = await response.json();
        
        // Fetch full results
        const resultsResponse = await fetch(`${API_BASE}/scan/${data.scan_id}`);
        const results = await resultsResponse.json();
        
        displayResults(results);
        
    } catch (error) {
        alert('Error processing image: ' + error.message);
        resetUpload();
    }
});

function displayResults(results) {
    // Hide loading
    loadingSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    
    // Display images
    document.getElementById('original-image').src = `/uploads/${results.original_image}`;
    document.getElementById('annotated-image').src = `/results/${results.processed_image}`;
    
    // Display stats
    document.getElementById('total-components').textContent = results.total_components;
    document.getElementById('total-value').textContent = `$${results.total_value.toFixed(2)}`;
    document.getElementById('recyclability-score').textContent = `${results.recyclability_score}/100`;
    
    // Display component table
    const tbody = document.getElementById('components-tbody');
    tbody.innerHTML = '';
    
    results.detections.forEach(det => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${det.component}</td>
            <td>${(det.confidence * 100).toFixed(1)}%</td>
            <td>$${det.estimated_value.toFixed(2)}</td>
        `;
    });
    
    // Update global stats
    fetchGlobalStats();
}

async function fetchGlobalStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const stats = await response.json();
        
        document.getElementById('global-scans').textContent = stats.total_scans;
        document.getElementById('global-components').textContent = stats.total_components_detected;
        document.getElementById('global-value').textContent = `$${stats.total_value_estimated.toFixed(2)}`;
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

function resetUpload() {
    selectedFile = null;
    imageInput.value = '';
    uploadArea.querySelector('.upload-content p').textContent = 'Drop image here or click to upload';
    analyzeBtn.disabled = true;
    
    uploadSection.classList.remove('hidden');
    loadingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
}

// Load stats on page load
fetchGlobalStats();