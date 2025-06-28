// static/mockup_script.js

/**
 * This is the main function that runs when the page is fully loaded.
 * It sets up the entire interactive mockup generator.
 */
function initializeMockupGenerator() {
    console.log("Initializing Mockup Generator...");

    // --- A: Get All DOM Elements ---
    const elements = {
        dataElement: document.getElementById('analysis-data'),
        domainDisplay: document.getElementById('domain-name-display'),
        colorPalette: document.getElementById('color-palette'),
        tabsContainer: document.querySelector('.template-tabs'),
        regenerateButton: document.getElementById('regenerate-button'),
        mockupOutput: document.getElementById('mockup-output'),
        loader: document.getElementById('mockup-loader'),
        cardControls: document.getElementById('card-controls'),
        tshirtControls: document.getElementById('tshirt-controls'),
        customNameInput: document.getElementById('custom-name'),
        customTitleInput: document.getElementById('custom-title'),
        customSloganInput: document.getElementById('custom-slogan'),
    };

    // --- B: Application State ---
    const state = {
        analysisData: null,
        activeTemplate: 'mug'
    };

    // --- C: Core Functions ---

    /**
     * Updates the UI to show the correct controls for the active template.
     */
    function updateActiveTemplate(template) {
        if (!template) return;
        state.activeTemplate = template;
        
        elements.tabsContainer.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.template === template);
        });

        elements.cardControls.style.display = (template === 'card') ? 'block' : 'none';
        elements.tshirtControls.style.display = (template === 'tshirt') ? 'block' : 'none';
        elements.mockupOutput.style.display = 'none'; // Hide old mockup before generating new one
    }

    /**
     * The main function to generate a new mockup by calling the backend.
     */
    async function generateMockup() {
        console.log(`Requesting mockup for: ${state.activeTemplate}`);
        elements.loader.style.display = 'block';
        elements.mockupOutput.style.display = 'none';

        const selectedColor = elements.colorPalette.querySelector('.color-box.active')?.dataset.color;
        if (!selectedColor) {
            alert("Error: No color selected!");
            elements.loader.style.display = 'none';
            return;
        }

        const requestBody = {
            logo_path: state.analysisData.base_analysis.logo_path,
            domain: state.analysisData.domain,
            new_color: selectedColor,
            active_template: state.activeTemplate,
            accent_color: state.analysisData.base_analysis.colors[1] || '#333333',
            custom_text: {
                name: elements.customNameInput.value,
                title: elements.customTitleInput.value,
                slogan: elements.customSloganInput.value
            }
        };

        try {
            const response = await fetch('/regenerate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody),
            });
            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.error || 'Server failed to generate the image file.');
            }
            updateMockupImage(result.data);
        } catch (error) {
            console.error("Regeneration failed:", error);
            alert("Error: " + error.message);
        } finally {
            elements.loader.style.display = 'none';
        }
    }

    /**
     * Updates the DOM to display the newly generated mockup image.
     */
    function updateMockupImage(resultData) {
        const timestamp = '?t=' + new Date().getTime();
        let title = `Generated ${state.activeTemplate.charAt(0).toUpperCase() + state.activeTemplate.slice(1)} Design`;
        if (resultData && resultData.design_path) {
            elements.mockupOutput.innerHTML = `
                <img src="${resultData.design_path + timestamp}" alt="${title}">
                <div class="item-info">
                    <h5>${title}</h5>
                    <a href="${resultData.pdf_path + timestamp}" download="${state.activeTemplate}_print_ready.pdf" class="download-button">
                        <i class="fa-solid fa-download"></i> Download PDF
                    </a>
                </div>`;
            elements.mockupOutput.style.display = 'flex';
        } else {
            elements.mockupOutput.style.display = 'none';
            alert('The backend successfully responded, but did not return a valid image path.');
        }
    }

    // --- D: Initialization ---
    
    // Step 1: Validate and parse the initial data from the server
    try {
        if (!elements.dataElement) throw new Error("Could not find analysis data element on page.");
        state.analysisData = JSON.parse(elements.dataElement.textContent);
        if (!state.analysisData || !state.analysisData.base_analysis) throw new Error("Analysis data is malformed.");
    } catch (e) {
        alert("Fatal Error: Could not read analysis data. Please start a new analysis. " + e.message);
        window.location.href = "/";
        return; // Stop execution if data is bad
    }
    
    // Step 2: Populate UI elements that depend on the initial data
    elements.domainDisplay.textContent = state.analysisData.domain;
    state.analysisData.base_analysis.colors.forEach((color, index) => {
        const colorBox = document.createElement('div');
        colorBox.className = 'color-box';
        colorBox.style.backgroundColor = color;
        colorBox.title = `Select color: ${color}`;
        colorBox.dataset.color = color;
        if (index === 0) colorBox.classList.add('active');
        elements.colorPalette.appendChild(colorBox);
    });

    // Step 3: Setup event listeners for all interactive elements
    elements.regenerateButton.addEventListener('click', generateMockup);
    elements.tabsContainer.addEventListener('click', (e) => {
        const tab = e.target.closest('.tab-button');
        if (tab) updateActiveTemplate(tab.dataset.template);
    });
    elements.colorPalette.addEventListener('click', (e) => {
        const colorBox = e.target.closest('.color-box');
        if (colorBox) {
            elements.colorPalette.querySelector('.active')?.classList.remove('active');
            colorBox.classList.add('active');
        }
    });

    // Step 4: Set the initial state of the UI and generate the first mockup
    updateActiveTemplate('mug');
    generateMockup();
}

// Start the entire process once the page is fully loaded.
window.addEventListener('DOMContentLoaded', initializeMockupGenerator);
