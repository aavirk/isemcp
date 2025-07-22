# ise_mcp_server.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP
import requests
import urllib3

# --- Print a version identifier to the logs ---
print("--- Running Script Version: ISE_V2_ENHANCED ---", file=sys.stderr)

# --- Find and Load the .env File ---
script_location = Path(__file__).resolve().parent
env_file_path = script_location / '.env'
load_dotenv(dotenv_path=env_file_path)

# --- Load Credentials ---
ISE_URL = os.getenv("ISE_URL")
ISE_USERNAME = os.getenv("ISE_USERNAME")
ISE_PASSWORD = os.getenv("ISE_PASSWORD")

# --- Disable SSL Warnings ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Cisco ISE API Connector Class ---
class CiscoISE_APIConnector:
    """Handles direct API communication with the Cisco ISE ERS and MNT APIs."""
    def __init__(self, base_url: str, username: str, password: str):
        if not all([base_url, username, password]):
            raise ValueError("Missing ISE_URL, ISE_USERNAME, or ISE_PASSWORD in .env file.")
        
        self.ers_base_url = f"{base_url.rstrip('/')}:9060/ers/config"
        self.mnt_base_url = f"{base_url.rstrip('/')}/admin/API/mnt" # Monitoring API has a different base
        self.auth = (username, password)
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.auth = self.auth
        self.session.verify = False

    def get(self, endpoint, api_type='ers', params=None):
        """Performs a GET request."""
        base_url = self.ers_base_url if api_type == 'ers' else self.mnt_base_url
        url = f"{base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, payload):
        """Performs a POST request."""
        url = f"{self.ers_base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

# --- Create the MCP Server ---
mcp = FastMCP(
    name="Cisco ISE MCP",
    instructions="An enhanced MCP server for Cisco ISE with read/write access for security groups, endpoints, and policies."
)

# --- Helper Function to Initialize the Connector ---
def get_connector():
    """Creates an instance of the CiscoISE_APIConnector."""
    return CiscoISE_APIConnector(ISE_URL, ISE_USERNAME, ISE_PASSWORD)

# --- Existing Tools ---
@mcp.tool()
def get_network_devices() -> dict:
    """Retrieves a list of all network devices from Cisco ISE."""
    try:
        connector = get_connector()
        return connector.get("networkdevice")
    except Exception as e:
        print(f"Error in get_network_devices tool: {e}", file=sys.stderr)
        return {"error": str(e)}

@mcp.tool()
def get_endpoints() -> dict:
    """Retrieves a list of all endpoints (connected devices) from Cisco ISE."""
    try:
        connector = get_connector()
        return connector.get("endpoint")
    except Exception as e:
        print(f"Error in get_endpoints tool: {e}", file=sys.stderr)
        return {"error": str(e)}

# --- NEW: Security Group Management Tools ---
@mcp.tool()
def get_security_groups() -> dict:
    """Retrieves all Security Group Tags (SGTs)."""
    try:
        connector = get_connector()
        return connector.get("sgt")
    except Exception as e:
        print(f"Error in get_security_groups tool: {e}", file=sys.stderr)
        return {"error": str(e)}

@mcp.tool()
def get_security_group_details(sgt_id: str) -> dict:
    """Retrieves details for a specific Security Group Tag (SGT) by its ID."""
    try:
        connector = get_connector()
        return connector.get(f"sgt/{sgt_id}")
    except Exception as e:
        print(f"Error in get_security_group_details tool: {e}", file=sys.stderr)
        return {"error": str(e)}

@mcp.tool()
def create_security_group(name: str, description: str, value: int) -> dict:
    """Creates a new Security Group Tag (SGT)."""
    try:
        connector = get_connector()
        payload = {"Sgt": {"name": name, "description": description, "value": value}}
        return connector.post("sgt", payload)
    except Exception as e:
        print(f"Error in create_security_group tool: {e}", file=sys.stderr)
        return {"error": str(e)}

# --- NEW: Endpoint Classification Tools ---
@mcp.tool()
def get_endpoint_groups() -> dict:
    """Retrieves all Endpoint Identity Groups."""
    try:
        connector = get_connector()
        return connector.get("endpointgroup")
    except Exception as e:
        print(f"Error in get_endpoint_groups tool: {e}", file=sys.stderr)
        return {"error": str(e)}

@mcp.tool()
def get_profiler_profiles() -> dict:
    """Retrieves all Profiler Profiles used for device classification."""
    try:
        connector = get_connector()
        return connector.get("profilerprofile")
    except Exception as e:
        print(f"Error in get_profiler_profiles tool: {e}", file=sys.stderr)
        return {"error": str(e)}

# --- NEW: Policy & Authorization Tools ---
@mcp.tool()
def get_authorization_profiles() -> dict:
    """Retrieves all Authorization Profiles."""
    try:
        connector = get_connector()
        return connector.get("authorizationprofile")
    except Exception as e:
        print(f"Error in get_authorization_profiles tool: {e}", file=sys.stderr)
        return {"error": str(e)}

@mcp.tool()
def get_active_sessions() -> dict:
    """Retrieves a list of all active sessions from the Monitoring node."""
    try:
        connector = get_connector()
        return connector.get("Session/ActiveList", api_type='mnt')
    except Exception as e:
        print(f"Error in get_active_sessions tool: {e}", file=sys.stderr)
        return {"error": str(e)}

# --- NEW: Enhanced Network Visibility Tools ---
@mcp.tool()
def get_network_device_groups() -> dict:
    """Retrieves all Network Device Groups."""
    try:
        connector = get_connector()
        return connector.get("networkdevicegroup")
    except Exception as e:
        print(f"Error in get_network_device_groups tool: {e}", file=sys.stderr)
        return {"error": str(e)}

@mcp.tool()
def get_endpoints_with_details() -> dict:
    """Retrieves a comprehensive list of endpoints with their group and SGT information."""
    try:
        connector = get_connector()
        endpoints = connector.get("endpoint").get("SearchResult", {}).get("resources", [])
        endpoint_groups = {g['id']: g['name'] for g in connector.get("endpointgroup").get("SearchResult", {}).get("resources", [])}
        sgts = {s['id']: s['name'] for s in connector.get("sgt").get("SearchResult", {}).get("resources", [])}

        detailed_endpoints = []
        for endpoint in endpoints:
            group_id = endpoint.get("groupId")
            sgt_id = endpoint.get("securityGroup")
            detailed_endpoints.append({
                "id": endpoint.get("id"),
                "name": endpoint.get("name"),
                "mac": endpoint.get("mac"),
                "description": endpoint.get("description"),
                "endpoint_group_name": endpoint_groups.get(group_id, "N/A"),
                "security_group_name": sgts.get(sgt_id, "N/A")
            })
        return {"endpoints": detailed_endpoints}
    except Exception as e:
        print(f"Error in get_endpoints_with_details tool: {e}", file=sys.stderr)
        return {"error": str(e)}

# --- Main Execution Block ---
if __name__ == "__main__":
    mcp.run()
