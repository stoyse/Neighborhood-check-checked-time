# Neighborhood Check

Neighborhood Check is a Flask-based web application that allows users to track and display check-in times, view statistics, and explore user data interactively on a map.

## Features

- **User-Specific Stats**: Users can save their username, and their stats are prominently displayed on the homepage.
- **Interactive Map**: Displays users grouped by airport on an interactive map using Leaflet.
- **Dark Mode**: Toggle between light and dark themes.
- **Fun Facts**: Generates fun facts based on user check-in times.
- **Scheduler**: Automatically updates data every 30 minutes using APScheduler.
- **Responsive Design**: Optimized for desktop and mobile devices.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/neighborhood-check.git
   cd neighborhood-check
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Ensure the database file is located at the path specified in `DB_PATH` in `app.py`.

5. Start the application:
   ```bash
   ./start_service.sh
   ```

6. Access the application at `http://localhost:8000`.

## Deployment

To deploy the application using Gunicorn:

1. Ensure Gunicorn is installed:
   ```bash
   pip install gunicorn
   ```

2. Start the application with Gunicorn:
   ```bash
   gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:application
   ```

3. Optionally, use a systemd service file for production deployment. See `start_Adventure-time.service` for an example.

## API Endpoints

- `/api/neighbors`: Returns all neighbors as JSON.
- `/api/stats`: Returns aggregated statistics as JSON.

## Interactive Map

The `/map` route displays an interactive map with users grouped by their airport. Airports are geocoded dynamically using the Nominatim API.

## Development

### Running Locally

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Run the Flask development server:
   ```bash
   python app.py
   ```

3. Access the application at `http://localhost:8923`.

### Testing

To test the application, use the Flask testing client or any HTTP client like Postman.

## File Structure

```
.
├── app.py                  # Main Flask application
├── wsgi.py                 # WSGI entry point for Gunicorn
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── start_service.sh        # Script to start the Gunicorn server
├── start_Adventure-time.service # Example systemd service file
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.