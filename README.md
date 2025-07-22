# ISE MCP Server

ISE MCP is a Python-based MCP (Model Context Protocol) server for Cisco's Identity Services Engine (ISE). This server provides comprehensive tools for querying the ISE API to discover, monitor, and manage your network access control infrastructure and security policies.

## Features

* **Network Device Management** - Discover and manage all network devices registered with ISE
* **Endpoint Discovery** - Monitor and manage all endpoints (connected devices) in your network
* **Security Group Management** - Create and manage Security Group Tags (SGTs) for network segmentation
* **Identity Group Management** - Monitor and manage Endpoint Identity Groups
* **Policy Management** - View and manage Authorization Profiles and Profiler Profiles
* **Session Monitoring** - Track active user and device sessions in real-time
* **Network Device Groups** - Organize and manage network device groupings
* **Comprehensive endpoint details** - Get detailed endpoint information including group and SGT assignments
* **Simple and extensible MCP server implementation**

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-repo/ise-mcp.git
cd ise-mcp
```

2. Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:

```bash
cp .env-example .env
```

2. Update the `.env` file with your ISE credentials:

```env
ISE_HOST="your-ise-host.example.com"
ISE_USERNAME="your-username"
ISE_PASSWORD="your-password"
ISE_VERIFY_SSL="false"  # Set to "true" for production environments
ISE_PORT="9060"  # Default ISE ERS API port
```

## Usage With Claude Desktop Client

1. Configure Claude Desktop to use this MCP server:
   * Open Claude Desktop
   * Go to Settings > Developer > Edit Config
   * Add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ISE_MCP": {
      "command": "/path/to/your/ise-mcp/.venv/bin/fastmcp",
      "args": [
        "run",
        "/path/to/your/ise-mcp/ise-mcp.py"
      ]
    }
  }
}
```

   * Replace the paths above to reflect your local environment

2. Restart Claude Desktop

3. Interact with Claude Desktop - you can now ask questions about your ISE deployment such as:
   * "What network devices are registered with ISE?"
   * "Show me all endpoints and their security group assignments"
   * "Create a new Security Group Tag for IoT devices"
   * "What active sessions do we have right now?"
   * "Show me all authorization profiles"
   * "What endpoint identity groups are configured?"

## Available Functions

The MCP server provides the following functions:

### Network Device Management
- `get_network_devices` - Retrieve a list of all network devices from ISE
- `get_network_device_groups` - Retrieve all Network Device Groups

### Endpoint Management
- `get_endpoints` - Retrieve a list of all endpoints (connected devices)
- `get_endpoints_with_details` - Get comprehensive endpoint information with group and SGT details
- `get_endpoint_groups` - Retrieve all Endpoint Identity Groups

### Security Group Management
- `get_security_groups` - Retrieve all Security Group Tags (SGTs)
- `get_security_group_details` - Get detailed information for a specific SGT by ID
- `create_security_group` - Create a new Security Group Tag

### Policy and Profile Management
- `get_profiler_profiles` - Retrieve all Profiler Profiles used for device classification
- `get_authorization_profiles` - Retrieve all Authorization Profiles

### Session Monitoring
- `get_active_sessions` - Retrieve a list of all active sessions from the Monitoring node

## Security Group Tag Management

The ISE MCP server supports creating new Security Group Tags (SGTs) for network segmentation. When creating an SGT, you need to provide:

- **Name**: A descriptive name for the SGT
- **Description**: Detailed description of the SGT's purpose
- **Value**: A unique numeric value for the SGT (typically between 2-65519)

Example usage through Claude:
"Create a new Security Group Tag called 'IoT_Devices' with description 'Internet of Things devices requiring restricted access' and value 1000"

## Session Monitoring

The active session monitoring provides real-time visibility into:
- Currently authenticated users and devices
- Session duration and status
- Authentication methods used
- Assigned policies and authorizations

## Prerequisites

* Cisco ISE deployment with ERS (External RESTful Services) API enabled
* ISE user account with appropriate API permissions:
  - ERS Admin or ERS Operator role
  - Access to required ISE nodes (Administration, Policy Service, Monitoring)
* Network connectivity to ISE on the configured port (default: 9060)

## Security Considerations

* Store your ISE credentials securely in the `.env` file
* Never commit credentials to version control
* Use dedicated service accounts with minimal required permissions
* Set `ISE_VERIFY_SSL="true"` in production environments
* Consider certificate-based authentication for enhanced security
* Regularly rotate API credentials

## Troubleshooting

If you encounter issues:

1. **Authentication Errors**:
   - Verify ISE credentials are correct
   - Ensure the user account has ERS API permissions
   - Check if the account is locked or expired

2. **Connection Issues**:
   - Verify network connectivity to ISE
   - Check if the ISE ERS API is enabled
   - Confirm the correct port (default: 9060)

3. **API Errors**:
   - Review ISE logs for detailed error information
   - Ensure ISE services are running properly
   - Check for any ISE maintenance windows

4. **Permission Errors**:
   - Verify user has appropriate ISE admin roles
   - Check Admin Groups assignments in ISE
   - Ensure access to required ISE personas (Admin, Policy, Monitoring)

## ISE API Limitations

Be aware of ISE API rate limits and best practices:
- ISE ERS API has built-in rate limiting
- Large deployments may require pagination for bulk operations
- Some operations may require specific ISE node types (Admin vs Policy vs Monitoring)
