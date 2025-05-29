import os
import requests
from datetime import datetime, timedelta
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class JuvonnoClient:
    """Client for interacting with the Juvonno EMR API."""
    
    def __init__(self, api_key=None, subdomain=None):
        """Initialize the Juvonno API client.
        
        Args:
            api_key (str): Juvonno API key
            subdomain (str): Juvonno subdomain
        """
        self.api_key = api_key or os.environ.get('JUVONNO_API_KEY')
        self.subdomain = subdomain or os.environ.get('JUVONNO_SUBDOMAIN')
        
        if not self.api_key:
            logger.warning("No Juvonno API key provided")
        
        if not self.subdomain:
            logger.warning("No Juvonno subdomain provided")
            
        # Clean up the subdomain to ensure proper formatting
        if self.subdomain:
            # Remove any protocol prefix if included
            if '://' in self.subdomain:
                self.subdomain = self.subdomain.split('://')[1]
                
            # Remove any trailing slashes
            self.subdomain = self.subdomain.rstrip('/')
                
            # Remove .juvonno.com if it was included in the subdomain
            if '.juvonno.com' in self.subdomain:
                self.subdomain = self.subdomain.replace('.juvonno.com', '')
            
            # Use the exact API URL format from the successful SwaggerHub test
            self.base_url = f"https://{self.subdomain}.juvonno.com/api"
            
        # Standard headers for Juvonno API with X-API-Key authentication
        self.headers = {
            'accept': 'application/json',
            'X-API-Key': self.api_key
        }
        
        # Empty auth params since we're using header authentication
        self.auth_params = {}
    
    def validate_credentials(self):
        """Validate the API credentials by making a simple API call.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # Use the exact working endpoint from your successful curl test
            url = f"{self.base_url}/branches"
            logger.debug(f"Validating credentials with URL: {url}")
            
            # Make request with X-API-Key in headers
            response = requests.get(url, headers=self.headers)
            
            # Log the response status for debugging
            logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"Authentication successful")
                return True
            elif response.status_code == 401:
                logger.warning(f"Authentication failed: Invalid API key")
                logger.debug(f"Response: {response.text}")
                return False
            else:
                logger.warning(f"Unexpected response: {response.status_code}")
                logger.debug(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error validating credentials: {str(e)}")
            return False
    
    def get_providers(self):
        """Get all providers from Juvonno.
        
        Returns:
            list: List of providers
        """
        try:
            # First validate credentials
            if not self.validate_credentials():
                logger.error("Cannot get providers: Invalid credentials")
                return []
                
            # According to working curl examples, use branches/options endpoint
            response = requests.get(
                f"{self.base_url}/branches/options", 
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get providers: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error getting providers: {str(e)}")
            return []
    
    def get_available_slots(self, start_date=None, end_date=None, provider_id=None):
        """Get available appointment slots.
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            provider_id (str): Provider ID
            
        Returns:
            list: List of available slots
        """
        try:
            # Default to searching 7 days from today if not specified
            if not start_date:
                start_date = datetime.now().strftime('%Y-%m-%d')
            if not end_date:
                end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            # Build query parameters with authentication
            params = self.auth_params.copy()  # Start with the api_key
            params.update({
                'start_date': start_date,
                'end_date': end_date
            })
            
            if provider_id:
                params['provider_id'] = provider_id
            
            # Use the format from successful curl example
            # Example: /api/appointments/availability/3?start_date=2025-05-22&end_date=2025-06-01
            if provider_id:
                url = f"{self.base_url}/appointments/availability/{provider_id}"
                # Remove provider_id from params since it's in the URL path
                if 'provider_id' in params:
                    del params['provider_id']
            else:
                url = f"{self.base_url}/appointments/availability"
                
            response = requests.get(
                url, 
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get available slots: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error getting available slots: {str(e)}")
            return []
    
    def book_appointment(self, appointment_data):
        """Book a new patient appointment.
        
        Args:
            appointment_data (dict): Appointment details
            
        Returns:
            dict: Booking result
        """
        try:
            patient_details = appointment_data.get('patient_details', {})
            
            # Create patient if doesn't exist
            patient_id = self._create_or_get_patient(patient_details)
            
            if not patient_id:
                raise Exception("Failed to create or retrieve patient")
            
            # Prepare appointment payload
            appointment_payload = {
                'patient_id': patient_id,
                'provider_id': appointment_data.get('provider_id'),
                'start_time': appointment_data.get('appointment_time'),
                'appointment_type_id': appointment_data.get('appointment_type'),
                'notes': appointment_data.get('notes', '')
            }
            
            # Book the appointment using header authentication
            response = requests.post(
                f"{self.base_url}/appointments",
                headers=self.headers,
                json=appointment_payload
            )
            
            if response.status_code == 201:  # 201 Created
                return response.json()
            else:
                logger.error(f"Failed to book appointment: {response.status_code} - {response.text}")
                raise Exception(f"Failed to book appointment: {response.text}")
                
        except Exception as e:
            logger.error(f"Error booking appointment: {str(e)}")
            raise
    
    def _create_or_get_patient(self, patient_details):
        """Create a new patient or get existing patient ID.
        
        Args:
            patient_details (dict): Patient information
            
        Returns:
            str: Patient ID
        """
        try:
            # Check if patient exists by email or phone
            email = patient_details.get('email')
            phone = patient_details.get('phone')
            
            if email:
                # Search by email with API key in query params (API v2.2.2)
                search_params = self.auth_params.copy()
                search_params['email'] = email
                response = requests.get(
                    f"{self.base_url}/patients/search",
                    headers=self.headers,
                    params=search_params
                )
                
                if response.status_code == 200:
                    patients = response.json()
                    if patients and len(patients) > 0:
                        return patients[0]['id']
            
            # Create new patient
            patient_payload = {
                'first_name': patient_details.get('first_name'),
                'last_name': patient_details.get('last_name'),
                'email': email,
                'phone': phone,
                'date_of_birth': patient_details.get('date_of_birth'),
                'gender': patient_details.get('gender', ''),
                'address': patient_details.get('address', ''),
                'city': patient_details.get('city', ''),
                'state': patient_details.get('state', ''),
                'postal_code': patient_details.get('postal_code', ''),
                'is_new_patient': True
            }
            
            # Remove None values
            patient_payload = {k: v for k, v in patient_payload.items() if v is not None}
            
            # Create patient with API key in query params
            response = requests.post(
                f"{self.base_url}/patients",
                headers=self.headers,
                params=self.auth_params,  # Add API key in URL
                json=patient_payload
            )
            
            if response.status_code == 201:  # 201 Created
                return response.json().get('id')
            else:
                logger.error(f"Failed to create patient: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating or getting patient: {str(e)}")
            return None
    
    def get_appointment_types(self):
        """Get available appointment types.
        
        Returns:
            list: List of appointment types
        """
        try:
            # Use correct endpoint for appointment types in API v2.2.2
            response = requests.get(
                f"{self.base_url}/appointments/types", 
                headers=self.headers,
                params=self.auth_params  # Add API key in URL
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get appointment types: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error getting appointment types: {str(e)}")
            return []
    
    def get_appointment(self, appointment_id):
        """Get appointment details.
        
        Args:
            appointment_id (str): Appointment ID
            
        Returns:
            dict: Appointment details
        """
        try:
            response = requests.get(
                f"{self.base_url}/appointments/{appointment_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get appointment: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting appointment: {str(e)}")
            return None
            
    def test_endpoint(self, endpoint, method='GET', params=None, data=None):
        """Generic method to test any Juvonno API endpoint.
        
        Args:
            endpoint (str): API endpoint path (without leading slash)
            method (str): HTTP method (GET, POST, PUT, DELETE)
            params (dict, optional): Query parameters
            data (dict, optional): Request body for POST/PUT requests
            
        Returns:
            dict: Response from the API
        """
        # Ensure valid credentials
        if not self.api_key or not self.subdomain:
            return {'error': 'API key and subdomain are required'}
        
        # Construct the URL, handling whether endpoint already has a leading slash
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Prepare headers - using the class-level headers
        headers = self.headers
        
        # Log the request details
        logger.debug(f"Testing Juvonno API endpoint: {method} {url}")
        if params:
            logger.debug(f"Query parameters: {params}")
        if data:
            logger.debug(f"Request body: {data}")
            
        try:
            # Make the request
            method = method.upper()
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, params=params, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, params=params, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params)
            else:
                return {'error': f'Unsupported HTTP method: {method}'}
                
            # Try to parse JSON response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {'raw_text': response.text}
                
            # Include HTTP status code
            result = {
                'status_code': response.status_code,
                'response': response_data
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error testing Juvonno API endpoint: {str(e)}")
            return {'error': str(e)}
