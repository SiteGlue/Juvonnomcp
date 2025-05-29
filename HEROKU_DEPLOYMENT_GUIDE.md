# Heroku Deployment Guide for Juvonno MCP Server

This guide walks you through deploying the Juvonno MCP server to Heroku and integrating it with Vapi.

## Prerequisites

1. Heroku account
2. Heroku CLI installed
3. Git repository
4. Juvonno API credentials
5. Vapi account

## Step 1: Prepare for Deployment

Copy these files to your deployment directory:
- `mcp_heroku_server.py` - Main server application
- `juvonno_api.py` - Juvonno API client
- `Procfile` - Heroku process configuration
- `heroku_requirements.txt` - Python dependencies (rename to requirements.txt)
- `runtime.txt` - Python version specification
- `app.json` - Heroku app configuration

## Step 2: Deploy to Heroku

```bash
# Create Heroku app
heroku create your-juvonno-mcp-server

# Set environment variables (optional - can be passed in API calls)
heroku config:set JUVONNO_API_KEY=your_api_key
heroku config:set JUVONNO_SUBDOMAIN=your_subdomain

# Deploy
git add .
git commit -m "Deploy Juvonno MCP server"
git push heroku main
```

Your server will be available at: `https://your-juvonno-mcp-server.herokuapp.com`

## Step 3: Test the Deployment

Test the health endpoint:
```bash
curl https://your-juvonno-mcp-server.herokuapp.com/
```

Test the tools endpoint:
```bash
curl https://your-juvonno-mcp-server.herokuapp.com/tools
```

## Step 4: Configure Vapi MCP Integration

According to Vapi's MCP documentation, add your MCP server to Vapi:

### Option A: Using Vapi Dashboard
1. Go to your Vapi dashboard
2. Navigate to MCP Servers section
3. Add new MCP server with URL: `https://your-juvonno-mcp-server.herokuapp.com`

### Option B: Using Vapi API
```bash
curl -X POST "https://api.vapi.ai/mcp-server" \
  -H "Authorization: Bearer YOUR_VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "juvonno-appointment-scheduler",
    "url": "https://your-juvonno-mcp-server.herokuapp.com",
    "description": "Juvonno appointment scheduling MCP server"
  }'
```

## Step 5: Use MCP Tools in Vapi Assistant

Once configured, your Vapi assistant can use these tools:

1. **get_locations_by_postal_code**
   - Find clinic locations near a postal code
   - Parameters: postal_code, subdomain, api_key

2. **get_providers_by_location**
   - Get healthcare providers at a location
   - Parameters: location_id, service_type, subdomain, api_key

3. **get_available_slots**
   - Get available appointment slots
   - Parameters: provider_id, start_date, end_date, subdomain, api_key

4. **book_appointment**
   - Book new patient appointments
   - Parameters: provider_id, appointment_time, appointment_type, patient_name, patient_email, patient_phone, subdomain, api_key

## Step 6: Configure Assistant Instructions

Update your Vapi assistant with these instructions:

```
You are an appointment scheduling assistant for healthcare clinics using Juvonno EMR.

Available MCP tools:
- get_locations_by_postal_code: Find clinic locations near a postal code
- get_providers_by_location: Get providers at a specific location for a service type
- get_available_slots: Check available appointment times
- book_appointment: Schedule new patient appointments

Workflow:
1. Ask for patient's postal code to find nearby locations
2. Ask for preferred service type (massage, chiropractic, physiotherapy)
3. Show available providers at the chosen location
4. Display available appointment slots
5. Collect patient information and book appointment

Always use the subdomain "medrehabgroup" and the provided API key for MedRehab Group locations.
```

## API Endpoints

Your deployed MCP server provides these endpoints:

- `GET /` - Health check
- `GET /tools` - List available tools (for MCP discovery)
- `POST /call-tool` - Main MCP tool execution endpoint
- `POST /get-locations` - Direct location lookup
- `POST /get-providers` - Direct provider lookup  
- `POST /book-appointment` - Direct appointment booking

## Security Notes

- API keys can be passed as parameters in tool calls
- Environment variables are optional for default values
- All communication uses HTTPS
- CORS is enabled for Vapi integration

## Monitoring

Monitor your Heroku app:
```bash
heroku logs --tail
heroku ps
```

## Scaling

For production use:
```bash
heroku ps:scale web=2
heroku addons:create papertrail  # For logging
```

This MCP server provides a standardized, scalable interface for Juvonno appointment scheduling that works seamlessly with Vapi's voice assistant platform.