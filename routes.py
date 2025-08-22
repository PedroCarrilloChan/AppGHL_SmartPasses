from flask import render_template, request, jsonify
import logging

def register_routes(app):
    """Register all application routes."""
    
    @app.route('/')
    def index():
        """Home page route."""
        logging.debug("Home page accessed")
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        """About page route."""
        logging.debug("About page accessed")
        return render_template('index.html', page_title="About", 
                             message="This is the about page. You can customize this content.")
    
    @app.route('/contact')
    def contact():
        """Contact page route."""
        logging.debug("Contact page accessed")
        return render_template('index.html', page_title="Contact", 
                             message="Get in touch with us! You can add a contact form here.")
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({"status": "healthy", "message": "Flask application is running"})
