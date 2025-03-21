# Deployment Guide for Bahtsul Masail Engine

## Prerequisites

- A cloud platform account (e.g., AWS, Google Cloud, or DigitalOcean)
- Domain name (optional but recommended)
- SSL certificate (recommended for production)
- PostgreSQL database service
- Node.js and npm installed on the deployment server
- Python 3.8+ installed on the deployment server

## Backend Deployment

### 1. Database Setup

1. Create a PostgreSQL database instance on your chosen cloud platform
2. Note down the following credentials:
   - Database host
   - Database port
   - Database name
   - Username
   - Password

### 2. Environment Configuration

1. Create a production `.env` file with the following variables:
   ```
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=your_db_port
   DB_NAME=your_db_name
   ```

### 3. Backend Setup

1. Clone the repository on your server
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Update CORS settings in `main.py` with your frontend domain
4. Set up a production WSGI server:
   ```bash
   pip install gunicorn
   ```
5. Create a systemd service or use a process manager like PM2 to run:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

## Frontend Deployment

### 1. Build the Frontend

1. Update the API endpoint in your frontend configuration to point to your production backend
2. Build the production bundle:
   ```bash
   npm install
   npm run build
   ```

### 2. Serve the Frontend

Option 1: Using Nginx (Recommended)
1. Install Nginx
2. Configure Nginx to serve the built files from the `dist` directory
3. Set up SSL certificate using Let's Encrypt

Option 2: Using a Static Hosting Service
1. Deploy the contents of the `dist` directory to a service like Netlify, Vercel, or AWS S3 + CloudFront

## Security Considerations

1. Enable HTTPS for both frontend and backend
2. Update CORS settings to only allow your frontend domain
3. Set up proper firewalls and security groups
4. Implement rate limiting
5. Use environment variables for sensitive data
6. Regular security updates and monitoring

## Monitoring and Maintenance

1. Set up logging for both frontend and backend
2. Configure monitoring tools (e.g., Sentry, NewRelic)
3. Set up automated backups for the database
4. Implement health checks
5. Set up alerting for critical issues

## Scaling Considerations

1. Use a load balancer if needed
2. Configure auto-scaling policies
3. Optimize database queries and implement caching
4. Use CDN for static assets
5. Monitor resource usage and scale accordingly