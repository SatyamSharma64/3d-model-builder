#!/bin/bash

# build_and_run.sh - Automated Blender MCP Container Setup

set -e

echo "🚀 Starting Blender MCP Docker Setup..."

# Check if addon.py exists
if [ ! -f "addon.py" ]; then
    echo "📥 Downloading addon.py from GitHub..."
    curl -L -o addon.py https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py
fi

# Create projects directory if it doesn't exist
mkdir -p projects

# Create necessary files if they don't exist
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found! Please ensure all files are in the same directory."
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t blender-mcp:latest .

# Stop and remove existing container if it exists
echo "🧹 Cleaning up existing containers..."
docker stop blender-mcp-container 2>/dev/null || true
docker rm blender-mcp-container 2>/dev/null || true

# Run the container
echo "🚀 Starting Blender MCP container..."
docker run -d \
    --name blender-mcp-container \
    -p 5901:5901 \
    -p 9876:9876 \
    -v "$(pwd)/projects:/workspace" \
    -v "$(pwd)/addon.py:/root/.config/blender/4.2/scripts/addons/blender_mcp.py" \
    blender-mcp:latest

echo "✅ Container started successfully!"
echo ""
echo "📋 Container Information:"
echo "   Container Name: blender-mcp-container"
echo "   VNC Access: localhost:5901"
echo "   MCP Server: localhost:8080 (if applicable)"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs: docker logs blender-mcp-container"
echo "   Access shell: docker exec -it blender-mcp-container /bin/bash"
echo "   Stop container: docker stop blender-mcp-container"
echo "   Start container: docker start blender-mcp-container"
echo ""
echo "🎯 The BlenderMCP addon should be automatically installed and ready!"

# Wait a moment for container to start
sleep 3

# Check if container is running
if docker ps | grep -q blender-mcp-container; then
    echo "✅ Container is running successfully!"
    echo "📝 Check the logs to see if the addon was installed:"
    echo "   docker logs blender-mcp-container"
else
    echo "❌ Container failed to start. Check logs:"
    echo "   docker logs blender-mcp-container"
fi