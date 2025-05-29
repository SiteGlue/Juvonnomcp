# Juvonno MCP Server

This MCP (Model Context Protocol) server provides standardized tools for appointment scheduling with Juvonno EMR systems. It exposes a clean API interface that can be used by various AI platforms and applications.

## Features

The MCP server provides the following tools:

- **get_locations_by_postal_code**: Find clinic locations near a postal code
- **get_providers_by_location**: Get healthcare providers at a specific location
- **get_available_slots**: Get available appointment slots for a provider
- **book_appointment**: Book a new patient appointment
- **get_appointment_types**: Get available appointment types

## Usage

### Starting the MCP Server

```bash
python start_mcp_server.py
```

Or directly:

```bash
python mcp_juvonno_server.py
```

### Required Environment Variables

- `JUVONNO_API_KEY`: Your Juvonno API key
- `JUVONNO_SUBDOMAIN`: Your Juvonno subdomain (e.g., 'medrehabgroup')

### Integration with AI Platforms

The MCP server follows the standard Model Context Protocol, making it compatible with:

- Claude Desktop
- Other MCP-compatible AI applications
- Custom applications using the MCP protocol

### Example Tool Calls

#### Find Locations
```json
{
  "name": "get_locations_by_postal_code",
  "arguments": {
    "postal_code": "L1V 1B5",
    "subdomain": "medrehabgroup",
    "api_key": "your-api-key"
  }
}
```

#### Get Providers
```json
{
  "name": "get_providers_by_location",
  "arguments": {
    "location_id": "4",
    "service_type": "massage",
    "subdomain": "medrehabgroup",
    "api_key": "your-api-key"
  }
}
```

#### Book Appointment
```json
{
  "name": "book_appointment",
  "arguments": {
    "provider_id": "123",
    "appointment_time": "2024-06-15T14:00:00",
    "appointment_type": "New Patient",
    "patient_name": "John Doe",
    "patient_email": "john@example.com",
    "patient_phone": "555-123-4567",
    "subdomain": "medrehabgroup",
    "api_key": "your-api-key"
  }
}
```

## Configuration

### Claude Desktop Integration

To use with Claude Desktop, add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "juvonno-appointment-scheduler": {
      "command": "python",
      "args": ["/path/to/mcp_juvonno_server.py"],
      "env": {
        "JUVONNO_API_KEY": "your-api-key",
        "JUVONNO_SUBDOMAIN": "your-subdomain"
      }
    }
  }
}
```

## Benefits of MCP Architecture

1. **Standardized Interface**: Uses the Model Context Protocol for consistent integration
2. **Platform Agnostic**: Works with any MCP-compatible AI platform
3. **Reusable**: Can be shared across different applications and use cases
4. **Secure**: API credentials are handled securely through environment variables
5. **Scalable**: Easy to extend with additional Juvonno API functionality

## Security Considerations

- API keys are passed as parameters or environment variables
- All communication follows MCP security standards
- No persistent storage of sensitive data
- Input validation on all tool calls

## Error Handling

The server provides comprehensive error handling with clear error messages:

- Missing parameters
- Authentication failures
- API communication errors
- Invalid data formats

All errors are returned in a standardized JSON format.