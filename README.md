# St. Sebastian's Major Archiepiscopal Shrine, Thazhekad

A professional, responsive website built with Flask, MongoDB, and Tailwind CSS.

## Features
- **Dynamic Home Page**: Announcements marquee, daily mass widget, and prayer request form.
- **Multilingual Support**: Toggle between English and Malayalam.
- **Admin Dashboard**: Full CRUD for Mass timings, Announcements, and Parish Council.
- **Historic Content**: Detailed history of the Thazhekad Sasanam and AD 800 lineage.
- **Premium Design**: Maroon and Gold theme with modern animations and glassmorphism.

## Tech Stack
- **Backend**: Python Flask
- **Database**: MongoDB
- **Frontend**: HTML5, Tailwind CSS (via CDN), Vanilla JavaScript
- **Templating**: Jinja2

## Getting Started

### Prerequisites
- Python 3.x
- MongoDB (Running locally or a cloud instance)

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables (optional):
   ```bash
   # Windows
   set MONGO_URI=mongodb://localhost:27017/thazhekad_church
   set SECRET_KEY=your-secret-key
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Access the website:
   - Public: `http://127.0.0.1:5000`
   - Admin: `http://127.0.0.1:5000/admin` (Login: `admin` / `admin123`)

## Project Structure
- `/static`: CSS, JS, and Images.
- `/templates`: HTML views (Layout, Public pages, Admin).
- `/data`: JSON files for translations and parish config.
- `app.py`: Main Flask server and database logic.
