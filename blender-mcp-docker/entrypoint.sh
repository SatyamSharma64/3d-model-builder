#!/bin/bash

# Create log directory if it doesn't exist
mkdir -p /var/log

# Start X virtual framebuffer with better settings
echo "Starting X virtual framebuffer..."
Xvfb :1 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
export DISPLAY=:1

# Wait for X server to start
sleep 3

# Start window manager
echo "Starting window manager..."
fluxbox &
sleep 2

# Install and enable the addon first (background mode)
# echo "Installing BlenderMCP addon..."
# blender --background --python /opt/startup_script.py 2>&1

echo "saving empty blend file..."
blender --background --save-as /opt/empty.blend


# Start VNC server for remote access
echo "Starting VNC server..."
x11vnc -display :1 -nopw -forever -shared -rfbport 5901 &

# Give VNC server time to start
sleep 2

echo "Starting Blender with GUI..."
echo "Display: $DISPLAY"
echo "Checking if userpref.py exists:"
ls -la /opt/userpref.py

# Test Blender version
echo "Testing Blender startup..."
blender --version

# Start Blender with GUI and user preferences
echo "Starting Blender with userpref.py..."
echo "Log will be written to /var/log/blender_gui.log"

# Use exec to replace the shell process, ensuring proper signal handling
exec blender /opt/empty.blend --python /opt/userpref.py 2>&1 | tee /var/log/blender_gui.log
