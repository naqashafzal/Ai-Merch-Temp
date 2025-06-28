# app.py

import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from datetime import datetime
from urllib.parse import urlparse
from src.website_analyzer import WebsiteAnalyzer
from src.ai_analyzer import AIAnalyzer
from src.template_generator import TemplateGenerator
from src.history_manager import HistoryManager

app = Flask(__name__)
app.secret_key = 'this-is-the-master-secret-key'

ASSETS_DIR = os.path.join(os.getcwd(), 'assets')
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

history_manager = HistoryManager()
ai_analyzer = AIAnalyzer()

@app.template_filter('format_datetime')
def format_datetime_filter(iso_string):
    """Jinja2 filter to format an ISO date string into a readable format."""
    try:
        dt_object = datetime.fromisoformat(iso_string)
        return dt_object.strftime('%B %d, %Y at %I:%M %p')
    except (ValueError, TypeError):
        return "Invalid date"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history_page():
    history_data = history_manager.get_history()
    return render_template('history.html', history=history_data)

@app.route('/report/<int:history_id>')
def report_page(history_id):
    history_data = history_manager.get_history()
    report_item = next((item for item in history_data if item.get('id') == history_id), None)
    if not report_item:
        return redirect(url_for('history_page'))
    return render_template('report.html', report=report_item)

@app.route('/mockup-generator')
def mockup_generator():
    analysis_data = session.get('latest_analysis_data', None)
    if not analysis_data:
        return redirect(url_for('index'))
    return render_template('mockup_generator.html', analysis_data=analysis_data)
    
@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    url = data.get('url')
    if not url: return jsonify({"error": "URL is required."}), 400
    
    print(f"\n--- Starting Analysis for: {url} ---")
    
    try:
        analyzer = WebsiteAnalyzer(url)
        
        print("Step 1: Fetching and parsing HTML...")
        if not analyzer.fetch_and_parse_html():
            return jsonify({"error": "Analysis failed: Could not fetch or parse the website's HTML."}), 500
        
        print("Step 2: Capturing screenshot...")
        screenshot_path = analyzer.capture_screenshot()
        if not screenshot_path:
            return jsonify({"error": "Analysis failed: Could not capture a screenshot. The site may be blocking automation."}), 500
        
        print("Step 3: Finding logo...")
        logo_path = analyzer.get_logo()
        if not logo_path:
            print("WARNING: No suitable logo found. Proceeding without a logo.")
        
        print("Step 4: Extracting colors...")
        source_image_for_colors = logo_path if logo_path else screenshot_path
        colors = analyzer.get_brand_colors(source_image_for_colors, 6)
        if not colors or len(colors) < 2:
            print("WARNING: Could not extract a full color palette. Using fallback colors.")
            colors = ['#7A5CFA', '#1A2238', '#FFFFFF', '#9DA3B0', '#3C4A5A']
        
        print("Step 5: Performing AI analysis...")
        ai_analysis = ai_analyzer.get_structured_analysis(screenshot_path, colors)
        # FINAL CHECK: Ensure the AI analysis returned a valid dictionary
        if not ai_analysis or "brand_aesthetics" not in ai_analysis:
             return jsonify({"error": "Analysis failed: The AI model could not return a valid analysis of the screenshot."}), 500

        print("--- Analysis Complete. Preparing response. ---")
        domain = urlparse(url if url.startswith('http') else 'https://' + url).netloc
        
        final_response = {
            "domain": domain,
            "base_analysis": {
                "screenshot_path": screenshot_path.replace(os.path.sep, '/'),
                "logo_path": logo_path.replace(os.path.sep, '/') if logo_path else None,
                "colors": colors,
                "ai_description": ai_analysis.get("brand_aesthetics", "AI analysis could not determine aesthetics."),
                "ai_recommendations": ai_analysis.get("design_recommendations", [])
            },
            "generator_url": url_for('mockup_generator')
        }
        
        session['latest_analysis_data'] = final_response
        history_manager.save_analysis(final_response)
        
        return jsonify(final_response)
        
    except Exception as e:
        print(f"CRITICAL ERROR in /generate route: {e}")
        return jsonify({"error": f"A critical server error occurred: {e}"}), 500

@app.route('/regenerate', methods=['POST'])
def regenerate():
    data = request.get_json()
    logo_path, domain, new_color = data.get('logo_path'), data.get('domain'), data.get('new_color')
    active_template = data.get('active_template')
    custom_text = data.get('custom_text', {})
    if not all([domain, new_color, active_template]):
        return jsonify({"error": "Missing data for regeneration."}), 400
    try:
        base_logo_path = os.path.join(os.getcwd(), logo_path) if logo_path else None
        domain_output_dir = os.path.join(OUTPUT_DIR, domain)
        generator = TemplateGenerator(domain_output_dir, domain)
        result = None
        accent_color = data.get('accent_color', '#333333')
        if active_template == 'mug':
            result = generator.create_mug_template(base_logo_path, new_color)
        elif active_template == 'card':
            result = generator.create_business_card_template(base_logo_path, new_color, accent_color, user_name=custom_text.get('name'), user_title=custom_text.get('title'))
        elif active_template == 'tshirt':
            result = generator.create_tshirt_template(base_logo_path, new_color, slogan_text=custom_text.get('slogan'))
        if result and result.get("design_path"):
            return jsonify({"success": True, "data": result})
        else:
            return jsonify({"error": f"Backend failed to generate template for {active_template}."}), 500
    except Exception as e:
        print(f"CRITICAL ERROR during regeneration: {e}")
        return jsonify({"error": "Failed to regenerate templates due to a server exception."}), 500

@app.route('/assets/<path:path>')
def serve_asset(path):
    return send_from_directory(ASSETS_DIR, path)

@app.route('/output/<path:path>')
def serve_output(path):
    return send_from_directory(OUTPUT_DIR, path)

if __name__ == '__main__':
    app.run(debug=True)