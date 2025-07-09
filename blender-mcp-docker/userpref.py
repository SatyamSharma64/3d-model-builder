import os
import traceback
import bpy
import addon_utils
import threading
import time
from bpy.app import handlers

# Global flag to ensure we only run once
_setup_complete = False

def setup_gui_workspace():
    """Set up the GUI workspace optimally for MCP usage"""
    try:
        print("🔧 Setting up GUI workspace...", flush=True)
        
        # Configure workspace
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.show_region_ui = True  # Show sidebar
                            space.show_region_toolbar = True  # Show toolbar
                    
                    # Make sure UI region is visible
                    for region in area.regions:
                        if region.type == 'UI':
                            region.width = 300  # Set sidebar width
        
        # Configure preferences for better UX
        prefs = bpy.context.preferences
        prefs.view.show_splash = False
        prefs.view.show_tooltips = True
        
        # Save preferences
        bpy.ops.wm.save_userpref()
        
        print("GUI workspace configured for BlenderMCP", flush=True)
        return True
        
    except Exception as e:
        print(f"GUI workspace setup error: {e}", flush=True)
        traceback.print_exc()
        return False
    
def install_and_enable_addon():
    """Install and enable the BlenderMCP addon with better error handling"""
    try:
        print("Installing and enabling BlenderMCP addon...", flush=True)
        
        addon_name = "blender_mcp"
        addon_path = "/root/.config/blender/4.2/scripts/addons/blender_mcp.py"
        
        # Check if addon file exists
        if not os.path.exists(addon_path):
            print(f"Addon file not found at {addon_path}", flush=True)
            return False
        
        print(f"Addon file found at {addon_path}", flush=True)
        
        # Refresh addons list
        bpy.ops.preferences.addon_refresh()
        
        # Try to enable the addon
        try:
            bpy.ops.preferences.addon_enable(module=addon_name)
            print(f"Addon '{addon_name}' enabled via operator", flush=True)
        except Exception as e:
            print(f"Operator failed: {e}", flush=True)
            # Fallback to addon_utils
            try:
                addon_utils.enable(addon_name)
                print(f"Addon '{addon_name}' enabled via addon_utils", flush=True)
            except Exception as e2:
                print(f"Both methods failed: {e2}", flush=True)
                return False
        
        # Verify addon is enabled
        if addon_name in bpy.context.preferences.addons.keys():
            print(f"Addon '{addon_name}' is confirmed enabled", flush=True)
        else:
            print(f"Addon '{addon_name}' may not be properly enabled", flush=True)
        
        # Save user preferences
        try:
            bpy.ops.wm.save_userpref()
            print("User preferences saved", flush=True)
        except Exception as e:
            print(f"Could not save preferences: {e}", flush=True)
        
        return True
        
    except Exception as e:
        print(f"Error installing addon: {e}", flush=True)
        traceback.print_exc()
        return False

def start_mcp_server():
    """Start the MCP server in a separate thread"""
    def server_thread():
        try:
            print("Waiting for GUI to be fully ready...", flush=True)
            # Wait longer for GUI to be ready
            time.sleep(8)
            
            # Check if MCP operators are available
            if hasattr(bpy.ops, 'blendermcp'):
                print("BlenderMCP operators found, starting server...", flush=True)
                
                # Enable Poly Haven if available
                # if hasattr(bpy.ops.blendermcp, 'toggle_poly_haven'):
                #     bpy.ops.blendermcp.toggle_poly_haven()
                #     print("Poly Haven enabled", flush=True)
                
                # Start the server if available
                if hasattr(bpy.ops.blendermcp, 'start_server'):
                    bpy.ops.blendermcp.start_server()
                    print("BlenderMCP server started successfully!", flush=True)
                elif hasattr(bpy.ops.blendermcp, 'connect_claude'):
                    bpy.ops.blendermcp.connect_claude()
                    print("Connected to Claude successfully!", flush=True)
                else:
                    print("MCP server operators not found, check addon", flush=True)
                    
            else:
                print("BlenderMCP operators not available", flush=True)
                
        except Exception as e:
            print(f"Error starting MCP server: {e}", flush=True)
            traceback.print_exc()
    
    # Start server in background thread
    server_thread_obj = threading.Thread(target=server_thread, daemon=True)
    server_thread_obj.start()
    print("MCP server startup initiated in background", flush=True)

def delayed_setup():
    """Main setup function that runs after Blender is fully loaded"""
    global _setup_complete
    
    if _setup_complete:
        return
    
    try:
        print("Setting up Blender GUI with MCP...", flush=True)
        print("Blender GUI is ready, running delayed setup...", flush=True)
        
        # Install and enable addon
        if install_and_enable_addon():
            print("Addon setup complete", flush=True)
        
        # Setup workspace
        # if setup_gui_workspace():
        #     print("Workspace setup complete", flush=True)
        
        # Start MCP server in background
        start_mcp_server()
        
        print("Blender GUI ready with BlenderMCP!", flush=True)
        print("Check the sidebar for the BlenderMCP panel", flush=True)
        
        _setup_complete = True
        
    except Exception as e:
        print(f"Error in delayed setup: {e}", flush=True)
        traceback.print_exc()
    
    # Remove the handler after running
    if delayed_setup in handlers.load_post:
        handlers.load_post.remove(delayed_setup)

def load_handler(dummy):
    """Handler that gets called when Blender finishes loading"""
    print("Load handler triggered", flush=True)
    # Use a timer to delay execution a bit more
    bpy.app.timers.register(delayed_setup, first_interval=2.0)

# Main execution
print("=== USERPREF.PY STARTING ===", flush=True)
print(f"Blender version: {bpy.app.version}", flush=True)
print(f"Background mode: {bpy.app.background}", flush=True)

if not bpy.app.background:
    print("GUI mode detected, registering load handler...", flush=True)
    # Register handler to run after Blender loads
    if load_handler not in handlers.load_post:
        handlers.load_post.append(load_handler)
        print("Handler registered successfully", flush=True)

    bpy.app.timers.register(delayed_setup, first_interval=4.0)
else:
    print("Background mode detected, running setup immediately", flush=True)
    # In background mode, run immediately
    delayed_setup()

print("=== USERPREF.PY REGISTRATION COMPLETE ===", flush=True)