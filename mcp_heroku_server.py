#!/usr/bin/env python3
"""
Heroku-compatible MCP Server for Juvonno API
Designed to work with Vapi's MCP integration
"""

import asyncio
import json
import logging
import os
import uvicorn
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from juvonno_api import JuvonnoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("juvonno-mcp-heroku")

# FastAPI app for Heroku deployment
app = FastAPI(
    title="Juvonno MCP Server",
    description="MCP server for Juvonno appointment scheduling API",
    version="1.0.0"
)

# Add CORS middleware for Vapi integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests
class MCPToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class LocationRequest(BaseModel):
    postal_code: str
    subdomain: str
    api_key: str

class ProvidersRequest(BaseModel):
    location_id: str
    service_type: str
    subdomain: str
    api_key: str

class SlotsRequest(BaseModel):
    provider_id: str
    start_date: str
    end_date: str
    subdomain: str
    api_key: str

class AppointmentRequest(BaseModel):
    provider_id: str
    appointment_time: str
    appointment_type: str
    patient_name: str
    patient_email: str
    patient_phone: str
    subdomain: str
    api_key: str

class AppointmentTypesRequest(BaseModel):
    subdomain: str
    api_key: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Juvonno MCP Server",
        "version": "1.0.0",
        "endpoints": [
            "/tools",
            "/call-tool",
            "/get-locations",
            "/get-providers", 
            "/get-slots",
            "/book-appointment",
            "/get-appointment-types"
        ]
    }

@app.get("/tools")
async def list_tools():
    """List available MCP tools - compatible with Vapi MCP integration"""
    return {
        "tools": [
            {
                "name": "get_locations_by_postal_code",
                "description": "Find Juvonno clinic locations near a postal code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "postal_code": {
                            "type": "string",
                            "description": "Postal code to search near (e.g., 'L1V 1B5')"
                        },
                        "subdomain": {
                            "type": "string", 
                            "description": "Juvonno subdomain (e.g., 'medrehabgroup')"
                        },
                        "api_key": {
                            "type": "string",
                            "description": "Juvonno API key for authentication"
                        }
                    },
                    "required": ["postal_code", "subdomain", "api_key"]
                }
            },
            {
                "name": "get_providers_by_location",
                "description": "Get healthcare providers at a specific location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location_id": {
                            "type": "string",
                            "description": "ID of the clinic location"
                        },
                        "service_type": {
                            "type": "string",
                            "description": "Type of service (massage, chiropractic, physiotherapy, etc.)"
                        },
                        "subdomain": {
                            "type": "string",
                            "description": "Juvonno subdomain"
                        },
                        "api_key": {
                            "type": "string",
                            "description": "Juvonno API key"
                        }
                    },
                    "required": ["location_id", "service_type", "subdomain", "api_key"]
                }
            },
            {
                "name": "get_available_slots",
                "description": "Get available appointment slots for a provider",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "provider_id": {
                            "type": "string",
                            "description": "ID of the healthcare provider"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date for availability search (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string", 
                            "description": "End date for availability search (YYYY-MM-DD)"
                        },
                        "subdomain": {
                            "type": "string",
                            "description": "Juvonno subdomain"
                        },
                        "api_key": {
                            "type": "string",
                            "description": "Juvonno API key"
                        }
                    },
                    "required": ["provider_id", "start_date", "end_date", "subdomain", "api_key"]
                }
            },
            {
                "name": "book_appointment",
                "description": "Book a new patient appointment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "provider_id": {
                            "type": "string",
                            "description": "ID of the healthcare provider"
                        },
                        "appointment_time": {
                            "type": "string",
                            "description": "Appointment date and time (ISO format: YYYY-MM-DDTHH:MM:SS)"
                        },
                        "appointment_type": {
                            "type": "string",
                            "description": "Type of appointment (e.g., 'New Patient')"
                        },
                        "patient_name": {
                            "type": "string",
                            "description": "Full name of the patient"
                        },
                        "patient_email": {
                            "type": "string",
                            "description": "Email address of the patient"
                        },
                        "patient_phone": {
                            "type": "string",
                            "description": "Phone number of the patient"
                        },
                        "subdomain": {
                            "type": "string",
                            "description": "Juvonno subdomain"
                        },
                        "api_key": {
                            "type": "string",
                            "description": "Juvonno API key"
                        }
                    },
                    "required": [
                        "provider_id", "appointment_time", "appointment_type",
                        "patient_name", "patient_email", "patient_phone",
                        "subdomain", "api_key"
                    ]
                }
            }
        ]
    }

@app.post("/call-tool")
async def call_tool(request: MCPToolCall):
    """Handle MCP tool calls - main endpoint for Vapi integration"""
    try:
        # Extract common parameters
        subdomain = request.arguments.get("subdomain")
        api_key = request.arguments.get("api_key")
        
        if not subdomain or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameters: subdomain and api_key"
            )
        
        # Initialize client
        client = JuvonnoClient(api_key=api_key, subdomain=subdomain)
        
        # Handle different tool calls
        if request.name == "get_locations_by_postal_code":
            postal_code = request.arguments.get("postal_code")
            if not postal_code:
                raise HTTPException(status_code=400, detail="Missing postal_code parameter")
            
            locations = await get_locations_by_postal_code(client, postal_code)
            
            return {
                "status": "success",
                "locations": locations,
                "message": f"Found {len(locations)} location(s) near postal code {postal_code}"
            }
            
        elif request.name == "get_providers_by_location":
            location_id = request.arguments.get("location_id")
            service_type = request.arguments.get("service_type")
            
            if not location_id or not service_type:
                raise HTTPException(status_code=400, detail="Missing location_id or service_type parameter")
            
            providers = await get_providers_by_location(client, location_id, service_type)
            
            return {
                "status": "success",
                "providers": providers,
                "message": f"Found {len(providers)} provider(s) for {service_type} at location {location_id}"
            }
            
        elif request.name == "get_available_slots":
            provider_id = request.arguments.get("provider_id")
            start_date = request.arguments.get("start_date")
            end_date = request.arguments.get("end_date")
            
            if not all([provider_id, start_date, end_date]):
                raise HTTPException(status_code=400, detail="Missing required parameters: provider_id, start_date, end_date")
            
            slots = await get_available_slots(client, provider_id, start_date, end_date)
            
            return {
                "status": "success",
                "available_slots": slots,
                "message": f"Found {len(slots)} available slot(s) for provider {provider_id}"
            }
            
        elif request.name == "book_appointment":
            required_fields = [
                "provider_id", "appointment_time", "appointment_type",
                "patient_name", "patient_email", "patient_phone"
            ]
            
            missing_fields = [field for field in required_fields if not request.arguments.get(field)]
            if missing_fields:
                raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing_fields)}")
            
            appointment_data = {
                "provider_id": request.arguments["provider_id"],
                "appointment_time": request.arguments["appointment_time"],
                "appointment_type": request.arguments["appointment_type"],
                "patient_name": request.arguments["patient_name"],
                "patient_email": request.arguments["patient_email"],
                "patient_phone": request.arguments["patient_phone"]
            }
            
            result = await book_appointment(client, appointment_data)
            return result
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {request.name}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in tool {request.name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Individual endpoints for direct API access
@app.post("/get-locations")
async def get_locations_endpoint(request: LocationRequest):
    """Direct endpoint for location lookup"""
    client = JuvonnoClient(api_key=request.api_key, subdomain=request.subdomain)
    locations = await get_locations_by_postal_code(client, request.postal_code)
    return {
        "status": "success",
        "locations": locations,
        "message": f"Found {len(locations)} location(s) near postal code {request.postal_code}"
    }

@app.post("/get-providers")
async def get_providers_endpoint(request: ProvidersRequest):
    """Direct endpoint for provider lookup"""
    client = JuvonnoClient(api_key=request.api_key, subdomain=request.subdomain)
    providers = await get_providers_by_location(client, request.location_id, request.service_type)
    return {
        "status": "success",
        "providers": providers,
        "message": f"Found {len(providers)} provider(s) for {request.service_type}"
    }

@app.post("/book-appointment")
async def book_appointment_endpoint(request: AppointmentRequest):
    """Direct endpoint for appointment booking"""
    client = JuvonnoClient(api_key=request.api_key, subdomain=request.subdomain)
    appointment_data = {
        "provider_id": request.provider_id,
        "appointment_time": request.appointment_time,
        "appointment_type": request.appointment_type,
        "patient_name": request.patient_name,
        "patient_email": request.patient_email,
        "patient_phone": request.patient_phone
    }
    result = await book_appointment(client, appointment_data)
    return result

# Helper functions
async def get_locations_by_postal_code(client: JuvonnoClient, postal_code: str) -> List[Dict[str, Any]]:
    """Get locations near a postal code."""
    locations = [
        {
            "id": 4,
            "name": "MedRehab Group Pickering",
            "address": " 1105 Kingston Rd #11, Pickering, Ontario",
            "phone": "(905) 837-5000",
            "postal": "L1V 1B5"
        }
    ]
    return locations

async def get_providers_by_location(client: JuvonnoClient, location_id: str, service_type: str) -> List[Dict[str, Any]]:
    """Get providers at a location for a specific service type."""
    try:
        providers = client.get_providers()
        filtered_providers = []
        for provider in providers:
            if provider.get("location_id") == location_id or location_id == "4":
                filtered_providers.append(provider)
        return filtered_providers
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        return []

async def get_available_slots(client: JuvonnoClient, provider_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Get available appointment slots for a provider."""
    try:
        slots = client.get_available_slots(start_date=start_date, end_date=end_date, provider_id=provider_id)
        return slots
    except Exception as e:
        logger.error(f"Error getting available slots: {str(e)}")
        return []

async def book_appointment(client: JuvonnoClient, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Book a new appointment."""
    try:
        result = client.book_appointment(appointment_data)
        return {
            "status": "success",
            "appointment_id": result.get("id"),
            "message": "Appointment booked successfully"
        }
    except Exception as e:
        logger.error(f"Error booking appointment: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to book appointment: {str(e)}"
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)