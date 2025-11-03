const imageInput = document.getElementById('imageInput');
const uploadArea = document.getElementById('uploadArea');
const uploadSection = document.getElementById('uploadSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const previewImage = document.getElementById('previewImage');
const analysisContent = document.getElementById('analysisContent');
const recommendationsCanvas = document.getElementById('recommendationsCanvas');

imageInput.addEventListener('change', handleFileSelect);
uploadArea.addEventListener('click', () => imageInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
        handleFile(files[0]);
    }
});

function handleFileSelect(e) {
    const file = e.target.files && e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (!file.type || !file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        if (e.target && e.target.result) {
            previewImage.src = e.target.result;
        }
    };
    reader.readAsDataURL(file);

    uploadImage(file);
}

async function uploadImage(file) {
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'none';
    loadingSection.style.display = 'block';

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        if (data && data.success) {
            displayResults(data);
        } else {
            alert((data && data.message) || 'Analysis failed. Please try again.');
            clearAnalysis();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
        clearAnalysis();
    }
}

function displayResults(data) {
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'block';

    const analysis = data.skin_analysis;
    if (!analysis) {
        alert('No analysis data received.');
        clearAnalysis();
        return;
    }

    const concernsHTML = Array.isArray(analysis.concerns)
        ? analysis.concerns.map(c => `<span class="concern-badge">${c}</span>`).join('')
        : '';
    const severityClass = analysis.severity ? `severity-${analysis.severity.toLowerCase()}` : '';

    analysisContent.innerHTML = `
        <div style="margin-bottom: 1.5rem;">
            <h4 style="margin-bottom: 0.5rem; color: var(--text-secondary);">Detected Concerns</h4>
            <div>${concernsHTML}</div>
        </div>
        <div style="margin-bottom: 1.5rem;">
            <h4 style="margin-bottom: 0.5rem; color: var(--text-secondary);">Severity Level</h4>
            <span class="severity-badge ${severityClass}">${analysis.severity || 'N/A'}</span>
        </div>
        <div style="margin-bottom: 1.5rem;">
            <h4 style="margin-bottom: 0.5rem; color: var(--text-secondary);">Skin Type</h4>
            <p style="font-weight: 500;">${analysis.skin_type || 'Unknown'}</p>
        </div>
        <div class="analysis-detail">
            <h4 style="margin-bottom: 0.5rem; color: var(--text-secondary);">Detailed Analysis</h4>
            <p>${analysis.analysis || 'No detailed analysis available.'}</p>
        </div>
        <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color);">
            <h4 style="margin-bottom: 0.5rem; color: var(--text-secondary);">Primary Concern</h4>
            <p style="font-weight: 600; color: var(--primary-color); text-transform: capitalize;">
                ${analysis.primary_concern || 'None'}
            </p>
        </div>
    `;

    displayRecommendations(data.recommendations);
}

function displayRecommendations(recommendations) {
    if (!Array.isArray(recommendations) || recommendations.length === 0) {
        recommendationsCanvas.innerHTML = `
            <div class="canvas-placeholder">
                <h3>No Recommendations Available</h3>
                <p>Unable to generate product recommendations at this time.</p>
            </div>
        `;
        return;
    }

    let recommendationsHTML = `
        <h2 style="margin-bottom: 1.5rem; color: var(--text-primary);">Recommended Products</h2>
    `;

    recommendations.forEach(product => {
        const highlightsHTML = Array.isArray(product.key_highlights)
            ? product.key_highlights.map(h => `<div class="highlight-item">${h}</div>`).join('')
            : '';

        recommendationsHTML += `
            <div class="product-card">
                <div class="product-header">
                    <div>
                        <div class="product-name">${product.name || 'Unnamed Product'}</div>
                        <div class="product-type">${product.type || ''}</div>
                    </div>
                    <div style="text-align: right;">
                        <div class="product-price">${product.price || ''}</div>
                        <div class="product-size">${product.size || ''}</div>
                    </div>
                </div>
                <div class="highlights">
                    <h4>Key Highlights</h4>
                    ${highlightsHTML}
                </div>
            </div>
        `;
    });

    recommendationsCanvas.innerHTML = recommendationsHTML;
}

function clearAnalysis() {
    uploadSection.style.display = 'block';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';

    recommendationsCanvas.innerHTML = `
        <div class="canvas-placeholder">
            <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            <h3>Product Recommendations</h3>
            <p>Upload a skin image to get personalized product recommendations</p>
        </div>
    `;

    imageInput.value = '';
}
