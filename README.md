# Juvonno MCP Server

A Model Context Protocol (MCP) server for Juvonno EMR appointment scheduling, designed for integration with Vapi voice assistants and other MCP-compatible platforms.

## Features

- **Location Discovery**: Find clinic locations by postal code
- **Provider Lookup**: Get healthcare providers by location and service type
- **Availability Checking**: Retrieve available appointment slots
- **Appointment Booking**: Schedule new patient appointments
- **Heroku Ready**: Configured for easy deployment to Heroku
- **Vapi Compatible**: Designed to work with Vapi's MCP integration

## Quick Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## API Endpoints

- `GET /` - Health check
- `GET /tools` - List available MCP tools
- `POST /call-tool` - Execute MCP tools (main endpoint for Vapi)
- `POST /get-locations` - Direct location lookup
- `POST /get-providers` - Direct provider lookup
- `POST /book-appointment` - Direct appointment booking

## Available MCP Tools

1. **get_locations_by_postal_code**
   - Find clinic locations near a postal code
   - Parameters: `postal_code`, `subdomain`, `api_key`

2. **get_providers_by_location**
   - Get healthcare providers at a specific location
   - Parameters: `location_id`, `service_type`, `subdomain`, `api_key`

3. **get_available_slots**
   - Get available appointment slots for a provider
   - Parameters: `provider_id`, `start_date`, `end_date`, `subdomain`, `api_key`

4. **book_appointment**
   - Book a new patient appointment
   - Parameters: `provider_id`, `appointment_time`, `appointment_type`, `patient_name`, `patient_email`, `patient_phone`, `subdomain`, `api_key`

## Environment Variables

Optional environment variables (can also be passed as parameters):

- `JUVONNO_API_KEY` - Your Juvonno API key
- `JUVONNO_SUBDOMAIN` - Your Juvonno subdomain

## Local Development

```bash
pip install -r requirements.txt
python mcp_heroku_server.py
```

Server runs on port 8000 by default.

## Deployment

See [HEROKU_DEPLOYMENT_GUIDE.md](HEROKU_DEPLOYMENT_GUIDE.md) for complete deployment instructions.

## Vapi Integration

Once deployed, add your Heroku app URL to Vapi's MCP server configuration:

```
https://your-app-name.herokuapp.com
```

## License

MIT License