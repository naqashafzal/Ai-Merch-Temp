// static/script.js

document.getElementById('generator-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const urlInput = document.getElementById('url-input');
    const loader = document.getElementById('loader');
    const resultsContainer = document.getElementById('results-container');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const nextStepSection = document.getElementById('next-step-section');

    // --- Reset UI ---
    loader.style.display = 'block';
    resultsContainer.style.display = 'none';
    errorContainer.style.display = 'none';
    nextStepSection.style.display = 'none';
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: urlInput.value }),
        });

        const data = await response.json();

        // This is the critical check. If the response is not OK (e.g., status 500),
        // we use the error message from the JSON body sent by the server.
        if (!response.ok) {
            throw new Error(data.error || 'An unknown server error occurred.');
        }

        // Also validate the structure of the successful response.
        if (!data.base_analysis) {
            throw new Error('Analysis returned incomplete data. The website may be complex or block automated tools.');
        }

        // If all checks pass, populate the results.
        populateAnalysisResults(data);

    } catch (error) {
        // This 'catch' block will now handle all failures gracefully.
        errorContainer.style.display = 'block';
        errorMessage.textContent = error.message;
    } finally {
        loader.style.display = 'none';
    }
});


function populateAnalysisResults(data) {
    const timestamp = '?t=' + new Date().getTime();
    const resultsContainer = document.getElementById('results-container');

    // Populate screenshot
    document.getElementById('screenshot-result-section').style.display = 'block';
    document.getElementById('screenshot-img').src = data.base_analysis.screenshot_path + timestamp;

    // Populate aesthetics and logo
    const logoImg = document.getElementById('logo-img');
    if (data.base_analysis.logo_path) {
        logoImg.src = data.base_analysis.logo_path + timestamp;
        logoImg.style.display = 'block';
    } else {
        logoImg.style.display = 'none';
    }
    document.getElementById('ai-description-text').textContent = data.base_analysis.ai_description;

    // Populate color palette
    const colorPalette = document.getElementById('color-palette');
    colorPalette.innerHTML = '';
    data.base_analysis.colors.forEach(color => {
        const colorBox = document.createElement('div');
        colorBox.className = 'color-box';
        colorBox.style.backgroundColor = color;
        colorBox.title = color;
        colorPalette.appendChild(colorBox);
    });

    // Populate AI recommendations
    const recommendationsCard = document.getElementById('recommendations-card');
    const recommendationsList = document.getElementById('ai-recommendations-list');
    recommendationsList.innerHTML = '';
    if (data.base_analysis.ai_recommendations && data.base_analysis.ai_recommendations.length > 0) {
        recommendationsCard.style.display = 'block';
        data.base_analysis.ai_recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="fa-solid fa-check"></i> ${rec}`;
            recommendationsList.appendChild(li);
        });
    } else {
        recommendationsCard.style.display = 'none';
    }
    
    // Activate and link the "Continue" button
    const nextStepBtn = document.getElementById('go-to-mockups-btn');
    const nextStepSection = document.getElementById('next-step-section');
    if (data.generator_url) {
        nextStepBtn.href = data.generator_url;
        nextStepSection.style.display = 'block';
    }

    resultsContainer.style.display = 'block';
}