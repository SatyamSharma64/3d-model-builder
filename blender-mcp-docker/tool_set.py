import json
import tempfile
import os
from pathlib import Path
import base64
from urllib.parse import urlparse
# from mcp.server.fastmcp import mcp
import logging
from blender_core import register_tool, register_prompt
from blender_server import get_blender_connection, _polyhaven_enabled


# Tool definitions with proper schemas
logger = logging.getLogger("BlenderMCPServer")

@register_tool(
    name="get_scene_info",
    description="Get detailed information about the current Blender scene including objects, materials, and scene properties",
    input_schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def get_scene_info(args: dict) -> str:
    """Get detailed information about the current Blender scene"""
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_scene_info")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting scene info from Blender: {str(e)}")
        return f"Error getting scene info: {str(e)}"

@register_tool(
    name="get_object_info",
    description="Get detailed information about a specific object in the Blender scene including location, scale, materials, and mesh data",
    input_schema={
        "type": "object",
        "properties": {
            "object_name": {
                "type": "string",
                "description": "Name of the object to get information about"
            }
        },
        "required": ["object_name"]
    }
)
def get_object_info(args: dict) -> str:
    """Get detailed information about a specific object in the Blender scene."""
    object_name = args.get('object_name')
    if not object_name:
        return "Error: object_name parameter is required"
    
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_object_info", {"name": object_name})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting object info from Blender: {str(e)}")
        return f"Error getting object info: {str(e)}"


@register_tool(
    name="export_model",
    description="export the 3d model after the generation task is completed",
    input_schema={
        "type": "object",
        "properties": {
            "export_format": {
                "type": "string",
                "description": "Model export type format"
            }
        },
        "required": ["export_format"]
    }
)
def export_model(args: dict) -> str:

    export_format = args.get('export_format')
    if not export_format:
        export_format = "GLB"
    # Export 
    try:
        blender = get_blender_connection()
        result = blender.send_command("export_model", {"export_format": export_format})
        return json.dumps(result)
        # decoded_data = base64.b64decode(base64_data)
        # print("Base64 data decoded successfully.")

        # # 2. Create a temporary directory
        # # This function returns the path to a newly created temporary directory.
        # # This directory will exist until explicitly removed or system reboot.
        # temp_dir = tempfile.mkdtemp()
        # print(f"Temporary directory created at: {temp_dir}")

        # # # 3. Determine the filename
        # # if filename is None:
        # #     # Generate a unique filename for the GLB model
        # unique_id = uuid.uuid4().hex
        # final_filename = f"temp_model_{unique_id}.glb"
        # # else:
        #     # Ensure the filename ends with .glb
        #     # if not filename.lower().endswith(".glb"):
        #     #     filename += ".glb"
        #     # final_filename = filename

        # # 4. Construct the full path for the GLB file
        # file_path = os.path.join(temp_dir, final_filename)

        # # 5. Write the binary data to the file
        # # Use 'wb' for writing binary data
        # with open(file_path, 'wb') as f:
        #     f.write(decoded_data)
        # print(f"GLB model successfully written to: {file_path}")
        
        # return f"Model Exported successfully and written to: {file_path}"
    except Exception as e:
        logger.error(f"Error exporting model from Blender: {str(e)}")
        return f"Error exporting model from Blender: {str(e)}"
    

@register_tool(
    name="get_viewport_screenshot",
    description="Capture a screenshot of the current Blender 3D viewport and return it as base64 encoded image data",
    input_schema={
        "type": "object",
        "properties": {
            "max_size": {
                "type": "integer",
                "description": "Maximum size for the screenshot (width or height, whichever is larger)",
                "default": 800,
                "minimum": 100,
                "maximum": 2048
            }
        },
        "required": []
    }
)
def get_viewport_screenshot(args: dict) -> str:
    """Capture a screenshot of the current Blender 3D viewport."""
    max_size = args.get('max_size', 800)
    
    try:
        blender = get_blender_connection()
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"blender_screenshot_{os.getpid()}.png")
        
        result = blender.send_command("get_viewport_screenshot", {
            "max_size": max_size,
            "filepath": temp_path,
            "format": "png"
        })
        
        if "error" in result:
            raise Exception(result["error"])
        
        if not os.path.exists(temp_path):
            raise Exception("Screenshot file was not created")
        
        # Read and encode the file as base64
        with open(temp_path, 'rb') as f:
            image_bytes = f.read()
        
        # Delete the temp file
        os.remove(temp_path)
        
        # Return base64 encoded image
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        return f"Screenshot captured successfully. Base64 data: data:image/png;base64,{image_b64}"
        
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}")
        return f"Screenshot failed: {str(e)}"

@register_tool(
    name="execute_blender_code",
    description="Execute arbitrary Python code in Blender's Python environment. Use this for creating objects, modifying scene, or any Blender operations",
    input_schema={
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute in Blender"
            }
        },
        "required": ["code"]
    }
)
def execute_blender_code(args: dict) -> str:
    """Execute arbitrary Python code in Blender."""
    code = args.get('code')
    if not code:
        return "Error: code parameter is required"
    
    try:
        blender = get_blender_connection()
        result = blender.send_command("execute_code", {"code": code})
        return f"Code executed successfully: {result.get('result', '')}"
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        return f"Error executing code: {str(e)}"

@register_tool(
    name="get_polyhaven_categories",
    description="Get a list of categories for a specific asset type on Polyhaven (hdris, textures, or models)",
    input_schema={
        "type": "object",
        "properties": {
            "asset_type": {
                "type": "string",
                "description": "Type of assets to get categories for",
                "enum": ["hdris", "textures", "models"],
                "default": "hdris"
            }
        },
        "required": []
    }
)
def get_polyhaven_categories(args: dict) -> str:
    """Get a list of categories for a specific asset type on Polyhaven."""
    asset_type = args.get('asset_type', 'hdris')
    
    try:
        blender = get_blender_connection()
        if not _polyhaven_enabled:
            return "PolyHaven integration is disabled. Select it in the sidebar in BlenderMCP, then run it again."
        
        result = blender.send_command("get_polyhaven_categories", {"asset_type": asset_type})
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        categories = result["categories"]
        formatted_output = f"Categories for {asset_type}:\n\n"
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_categories:
            formatted_output += f"- {category}: {count} assets\n"
        
        return formatted_output
    except Exception as e:
        logger.error(f"Error getting Polyhaven categories: {str(e)}")
        return f"Error getting Polyhaven categories: {str(e)}"

@register_tool(
    name="search_polyhaven_assets",
    description="Search for assets on Polyhaven with optional filtering by asset type and categories",
    input_schema={
        "type": "object",
        "properties": {
            "asset_type": {
                "type": "string",
                "description": "Type of assets to search for",
                "enum": ["all", "hdris", "textures", "models"],
                "default": "all"
            },
            "categories": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of categories to filter by (optional)"
            }
        },
        "required": []
    }
)
def search_polyhaven_assets(args: dict) -> str:
    """Search for assets on Polyhaven with optional filtering."""
    asset_type = args.get('asset_type', 'all')
    categories = args.get('categories')
    
    try:
        blender = get_blender_connection()
        result = blender.send_command("search_polyhaven_assets", {
            "asset_type": asset_type,
            "categories": categories
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        assets = result["assets"]
        total_count = result["total_count"]
        returned_count = result["returned_count"]
        
        formatted_output = f"Found {total_count} assets"
        if categories:
            formatted_output += f" in categories: {categories}"
        formatted_output += f"\nShowing {returned_count} assets:\n\n"
        
        sorted_assets = sorted(assets.items(), key=lambda x: x[1].get("download_count", 0), reverse=True)
        
        for asset_id, asset_data in sorted_assets:
            formatted_output += f"- {asset_data.get('name', asset_id)} (ID: {asset_id})\n"
            formatted_output += f"  Type: {['HDRI', 'Texture', 'Model'][asset_data.get('type', 0)]}\n"
            formatted_output += f"  Categories: {', '.join(asset_data.get('categories', []))}\n"
            formatted_output += f"  Downloads: {asset_data.get('download_count', 'Unknown')}\n\n"
        
        return formatted_output
    except Exception as e:
        logger.error(f"Error searching Polyhaven assets: {str(e)}")
        return f"Error searching Polyhaven assets: {str(e)}"

@register_tool(
    name="download_polyhaven_asset",
    description="Download and import a Polyhaven asset into Blender (HDRI, texture, or model)",
    input_schema={
        "type": "object",
        "properties": {
            "asset_id": {
                "type": "string",
                "description": "ID of the asset to download"
            },
            "asset_type": {
                "type": "string",
                "description": "Type of asset to download",
                "enum": ["hdris", "textures", "models"]
            },
            "resolution": {
                "type": "string",
                "description": "Resolution to download",
                "enum": ["1k", "2k", "4k", "8k", "16k"],
                "default": "1k"
            },
            "file_format": {
                "type": "string",
                "description": "File format to download (depends on asset type)"
            }
        },
        "required": ["asset_id", "asset_type"]
    }
)
def download_polyhaven_asset(args: dict) -> str:
    """Download and import a Polyhaven asset into Blender."""
    asset_id = args.get('asset_id')
    asset_type = args.get('asset_type')
    resolution = args.get('resolution', '1k')
    file_format = args.get('file_format')
    
    if not asset_id or not asset_type:
        return "Error: asset_id and asset_type parameters are required"
    
    try:
        blender = get_blender_connection()
        result = blender.send_command("download_polyhaven_asset", {
            "asset_id": asset_id,
            "asset_type": asset_type,
            "resolution": resolution,
            "file_format": file_format
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            message = result.get("message", "Asset downloaded and imported successfully")
            
            if asset_type == "hdris":
                return f"{message}. The HDRI has been set as the world environment."
            elif asset_type == "textures":
                material_name = result.get("material", "")
                maps = ", ".join(result.get("maps", []))
                return f"{message}. Created material '{material_name}' with maps: {maps}."
            elif asset_type == "models":
                return f"{message}. The model has been imported into the current scene."
            else:
                return message
        else:
            return f"Failed to download asset: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error downloading Polyhaven asset: {str(e)}")
        return f"Error downloading Polyhaven asset: {str(e)}"

@register_tool(
    name="search_sketchfab_models",
    description="Search for downloadable 3D models on Sketchfab with query and optional category filtering",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for models"
            },
            "categories": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of categories to filter by (optional)"
            },
            "count": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 20,
                "minimum": 1,
                "maximum": 100
            },
            "downloadable": {
                "type": "boolean",
                "description": "Only return downloadable models",
                "default": True
            }
        },
        "required": ["query"]
    }
)

def search_sketchfab_models(args: dict) -> str:
    """Search for models on Sketchfab with optional filtering."""
    query = args.get('query')
    categories = args.get('categories')
    count = args.get('count', 20)
    downloadable = args.get('downloadable', True)
    
    if not query:
        return "Error: query parameter is required"
    
    try:
        blender = get_blender_connection()
        result = blender.send_command("search_sketchfab_models", {
            "query": query,
            "categories": categories,
            "count": count,
            "downloadable": downloadable
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        models = result.get("results", []) or []
        if not models:
            return f"No models found matching '{query}'"
        
        formatted_output = f"Found {len(models)} models matching '{query}':\n\n"
        
        for model in models:
            if model is None:
                continue
            
            model_name = model.get("name", "Unnamed model")
            model_uid = model.get("uid", "Unknown ID")
            formatted_output += f"- {model_name} (UID: {model_uid})\n"
            
            user = model.get("user") or {}
            username = user.get("username", "Unknown author") if isinstance(user, dict) else "Unknown author"
            formatted_output += f"  Author: {username}\n"
            
            license_data = model.get("license") or {}
            license_label = license_data.get("label", "Unknown") if isinstance(license_data, dict) else "Unknown"
            formatted_output += f"  License: {license_label}\n"
            
            face_count = model.get("faceCount", "Unknown")
            is_downloadable = "Yes" if model.get("isDownloadable") else "No"
            formatted_output += f"  Face count: {face_count}\n"
            formatted_output += f"  Downloadable: {is_downloadable}\n\n"
        
        return formatted_output
    except Exception as e:
        logger.error(f"Error searching Sketchfab models: {str(e)}")
        return f"Error searching Sketchfab models: {str(e)}"

@register_tool(
    name="download_sketchfab_model",
    description="Download and import a Sketchfab model by its unique identifier (UID)",
    input_schema={
        "type": "object",
        "properties": {
            "uid": {
                "type": "string",
                "description": "Unique identifier of the Sketchfab model to download"
            }
        },
        "required": ["uid"]
    }
)
def download_sketchfab_model(args: dict) -> str:
    """Download and import a Sketchfab model by its UID."""
    uid = args.get('uid')
    
    if not uid:
        return "Error: uid parameter is required"
    
    try:
        blender = get_blender_connection()
        result = blender.send_command("download_sketchfab_model", {"uid": uid})
        
        if result is None:
            return "Error: Received no response from Sketchfab download request"
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            imported_objects = result.get("imported_objects", [])
            object_names = ", ".join(imported_objects) if imported_objects else "none"
            return f"Successfully imported model. Created objects: {object_names}"
        else:
            return f"Failed to download model: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error downloading Sketchfab model: {str(e)}")
        return f"Error downloading Sketchfab model: {str(e)}"

            
def _process_bbox(original_bbox):
    if original_bbox is None:
        return None
    if all(isinstance(i, int) for i in original_bbox):
        return original_bbox
    if any(i <= 0 for i in original_bbox):
        raise ValueError("Incorrect number range: bbox must be bigger than zero!")
    return [int(float(i) / max(original_bbox) * 100) for i in original_bbox] if original_bbox else None


@register_tool(
    name="generate_hyper3d_model_via_text",
    description="Generate a 3D model using Hyper3D Rodin AI by providing a text description",
    input_schema={
        "type": "object",
        "properties": {
            "text_prompt": {
                "type": "string",
                "description": "Text description of the 3D model to generate"
            },
            "bbox_condition": {
                "type": "array",
                "items": {
                    "type": "number"
                },
                "description": "Optional bounding box condition as [width, height, depth]",
                "minItems": 3,
                "maxItems": 3
            }
        },
        "required": ["text_prompt"],
    }
)


@register_tool("generate_hyper3d_model_via_text")
def generate_hyper3d_model_via_text(args: dict) -> str:
    """Generate 3D asset using Hyper3D by giving description of the desired asset."""
    text_prompt = args.get('text_prompt')
    bbox_condition = args.get('bbox_condition')
    
    if not text_prompt:
        return "Error: text_prompt parameter is required"
    
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_rodin_job", {
            "text_prompt": text_prompt,
            "images": None,
            "bbox_condition": _process_bbox(bbox_condition),
        })
        
        succeed = result.get("submit_time", False)
        if succeed:
            return json.dumps({
                "task_uuid": result["uuid"],
                "subscription_key": result["jobs"]["subscription_key"],
            })
        else:
            return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"

@register_tool(
    name="generate_hyper3d_model_via_images",
    description="Generate a 3D model using Hyper3D Rodin AI by providing reference images",
    input_schema={
        "type": "object",
        "properties": {
            "input_image_paths": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of local file paths to input images (cannot be used with input_image_urls)"
            },
            "input_image_urls": {
                "type": "array",
                "items": {
                    "type": "string",
                    "format": "uri"
                },
                "description": "List of URLs to input images (cannot be used with input_image_paths)"
            },
            "bbox_condition": {
                "type": "array",
                "items": {
                    "type": "number"
                },
                "description": "Optional bounding box condition as [width, height, depth]",
                "minItems": 3,
                "maxItems": 3
            }
        },
        "required": [],
        "oneOf": [
            {"required": ["input_image_paths"]},
            {"required": ["input_image_urls"]}
        ]
    }
)
def generate_hyper3d_model_via_images(args: dict) -> str:
    """Generate 3D asset using Hyper3D by giving images of the wanted asset."""
    input_image_paths = args.get('input_image_paths')
    input_image_urls = args.get('input_image_urls')
    bbox_condition = args.get('bbox_condition')
    
    if input_image_paths is not None and input_image_urls is not None:
        return "Error: Conflict parameters given!"
    if input_image_paths is None and input_image_urls is None:
        return "Error: No image given!"
    
    if input_image_paths is not None:
        if not all(os.path.exists(i) for i in input_image_paths):
            return "Error: not all image paths are valid!"
        images = []
        for path in input_image_paths:
            with open(path, "rb") as f:
                images.append(
                    (Path(path).suffix, base64.b64encode(f.read()).decode("ascii"))
                )
    elif input_image_urls is not None:
        if not all(urlparse(i) for i in input_image_urls):
            return "Error: not all image URLs are valid!"
        images = input_image_urls.copy()
    
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_rodin_job", {
            "text_prompt": None,
            "images": images,
            "bbox_condition": _process_bbox(bbox_condition),
        })
        
        succeed = result.get("submit_time", False)
        if succeed:
            return json.dumps({
                "task_uuid": result["uuid"],
                "subscription_key": result["jobs"]["subscription_key"],
            })
        else:
            return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"

@register_tool(
    name="poll_rodin_job_status",
    description="Check the status of a Hyper3D Rodin generation task to see if it's completed",
    input_schema={
        "type": "object",
        "properties": {
            "subscription_key": {
                "type": "string",
                "description": "Subscription key for the generation task (cannot be used with request_id)"
            },
            "request_id": {
                "type": "string",
                "description": "Request ID for the generation task (cannot be used with subscription_key)"
            }
        },
        "required": [],
        "oneOf": [
            {"required": ["subscription_key"]},
            {"required": ["request_id"]}
        ]
    }
)
def poll_rodin_job_status(args: dict) -> str:
    """Check if the Hyper3D Rodin generation task is completed."""
    subscription_key = args.get('subscription_key')
    request_id = args.get('request_id')
    
    try:
        blender = get_blender_connection()
        kwargs = {}
        if subscription_key:
            kwargs = {"subscription_key": subscription_key}
        elif request_id:
            kwargs = {"request_id": request_id}
        
        result = blender.send_command("poll_rodin_job_status", kwargs)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error polling Hyper3D task: {str(e)}")
        return f"Error polling Hyper3D task: {str(e)}"

@register_tool(
    name="import_generated_asset",
    description="Import the 3D asset generated by Hyper3D Rodin after the generation task is completed",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name to give the imported asset in Blender"
            },
            "task_uuid": {
                "type": "string",
                "description": "UUID of the generation task (cannot be used with request_id)"
            },
            "request_id": {
                "type": "string",
                "description": "Request ID of the generation task (cannot be used with task_uuid)"
            }
        },
        "required": ["name"],
        "oneOf": [
            {"required": ["name", "task_uuid"]},
            {"required": ["name", "request_id"]}
        ]
    }
)
def import_generated_asset(args: dict) -> str:
    """Import the asset generated by Hyper3D Rodin after the generation task is completed."""
    name = args.get('name')
    task_uuid = args.get('task_uuid')
    request_id = args.get('request_id')
    
    if not name:
        return "Error: name parameter is required"
    
    try:
        blender = get_blender_connection()
        kwargs = {"name": name}
        if task_uuid:
            kwargs["task_uuid"] = task_uuid
        elif request_id:
            kwargs["request_id"] = request_id
        
        result = blender.send_command("import_generated_asset", kwargs)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error importing generated asset: {str(e)}")
        return f"Error importing generated asset: {str(e)}"


# Add the prompt registry with proper schema

# @register_prompt(
#     name="asset_creation_strategy",
#     description="Defines the preferred strategy for creating assets in Blender using available integrations"
# )
# def asset_creation_strategy() -> str:
#     """Defines the preferred strategy for creating assets in Blender"""
#     return """When creating 3D content in Blender, always start by checking if integrations are available:

#     0. Before anything, always check the scene from get_scene_info()
#     1. First use the following tools to verify if the following integrations are enabled:
#         1. PolyHaven
#             Use get_polyhaven_status() to verify its status
#             If PolyHaven is enabled:
#             - For objects/models: Use download_polyhaven_asset() with asset_type="models"
#             - For materials/textures: Use download_polyhaven_asset() with asset_type="textures"
#             - For environment lighting: Use download_polyhaven_asset() with asset_type="hdris"
#         2. Sketchfab
#             Sketchfab is good at Realistic models, and has a wider variety of models than PolyHaven.
#             Use get_sketchfab_status() to verify its status
#             If Sketchfab is enabled:
#             - For objects/models: First search using search_sketchfab_models() with your query
#             - Then download specific models using download_sketchfab_model() with the UID
#             - Note that only downloadable models can be accessed, and API key must be properly configured
#             - Sketchfab has a wider variety of models than PolyHaven, especially for specific subjects
#         3. Hyper3D(Rodin)
#             Hyper3D Rodin is good at generating 3D models for single item.
#             So don't try to:
#             1. Generate the whole scene with one shot
#             2. Generate ground using Hyper3D
#             3. Generate parts of the items separately and put them together afterwards

#             Use get_hyper3d_status() to verify its status
#             If Hyper3D is enabled:
#             - For objects/models, do the following steps:
#                 1. Create the model generation task
#                     - Use generate_hyper3d_model_via_images() if image(s) is/are given
#                     - Use generate_hyper3d_model_via_text() if generating 3D asset using text prompt
#                     If key type is free_trial and insufficient balance error returned, tell the user that the free trial key can only generated limited models everyday, they can choose to:
#                     - Wait for another day and try again
#                     - Go to hyper3d.ai to find out how to get their own API key
#                     - Go to fal.ai to get their own private API key
#                 2. Poll the status
#                     - Use poll_rodin_job_status() to check if the generation task has completed or failed
#                 3. Import the asset
#                     - Use import_generated_asset() to import the generated GLB model the asset
#                 4. After importing the asset, ALWAYS check the world_bounding_box of the imported mesh, and adjust the mesh's location and size
#                     Adjust the imported mesh's location, scale, rotation, so that the mesh is on the right spot.

#                 You can reuse assets previous generated by running python code to duplicate the object, without creating another generation task.

#     3. Always check the world_bounding_box for each item so that:
#         - Ensure that all objects that should not be clipping are not clipping.
#         - Items have right spatial relationship.
    
#     4. Recommended asset source priority:
#         - For specific existing objects: First try Sketchfab, then PolyHaven
#         - For generic objects/furniture: First try PolyHaven, then Sketchfab
#         - For custom or unique items not available in libraries: Use Hyper3D Rodin
#         - For environment lighting: Use PolyHaven HDRIs
#         - For materials/textures: Use PolyHaven textures

#     Only fall back to scripting when:
#     - PolyHaven, Sketchfab, and Hyper3D are all disabled
#     - A simple primitive is explicitly requested
#     - No suitable asset exists in any of the libraries
#     - Hyper3D Rodin failed to generate the desired asset
#     - The task specifically requires a basic material/color
#     """

@register_prompt("asset_creation_strategy")
def asset_creation_strategy() -> str:
    """Defines the preferred strategy for creating assets in Blender"""
    return """You are a 3D creation agent with access to multiple Blender tools.

    Your job is to understand the user prompt, plan a sequence of tool calls, and generate a 3D scene accordingly.
    
    When creating 3D content in Blender, always start by checking if integrations are available:

    0. Before anything, always check the scene from get_scene_info()
    1. First use the following tools to verify if the following integrations are enabled:
        1. PolyHaven
            Use get_polyhaven_status() to verify its status
            If PolyHaven is enabled:
            - For objects/models: Use download_polyhaven_asset() with asset_type="models"
            - For materials/textures: Use download_polyhaven_asset() with asset_type="textures"
            - For environment lighting: Use download_polyhaven_asset() with asset_type="hdris"
        2. Sketchfab
            Sketchfab is good at Realistic models, and has a wider variety of models than PolyHaven.
            Use get_sketchfab_status() to verify its status
            If Sketchfab is enabled:
            - For objects/models: First search using search_sketchfab_models() with your query
            - Then download specific models using download_sketchfab_model() with the UID
            - Note that only downloadable models can be accessed, and API key must be properly configured
            - Sketchfab has a wider variety of models than PolyHaven, especially for specific subjects
        3. Hyper3D(Rodin)
            Hyper3D Rodin is good at generating 3D models for single item.
            So don't try to:
            1. Generate the whole scene with one shot
            2. Generate ground using Hyper3D
            3. Generate parts of the items separately and put them together afterwards

            Use get_hyper3d_status() to verify its status
            If Hyper3D is enabled:
            - For objects/models, do the following steps:
                1. Create the model generation task
                    - Use generate_hyper3d_model_via_images() if image(s) is/are given
                    - Use generate_hyper3d_model_via_text() if generating 3D asset using text prompt
                    If key type is free_trial and insufficient balance error returned, tell the user that the free trial key can only generated limited models everyday, they can choose to:
                    - Wait for another day and try again
                    - Go to hyper3d.ai to find out how to get their own API key
                    - Go to fal.ai to get their own private API key
                2. Poll the status
                    - Use poll_rodin_job_status() to check if the generation task has completed or failed
                3. Import the asset
                    - Use import_generated_asset() to import the generated GLB model the asset
                4. After importing the asset, ALWAYS check the world_bounding_box of the imported mesh, and adjust the mesh's location and size
                    Adjust the imported mesh's location, scale, rotation, so that the mesh is on the right spot.

                You can reuse assets previous generated by running python code to duplicate the object, without creating another generation task.

    3. Always check the world_bounding_box for each item so that:
        - Ensure that all objects that should not be clipping are not clipping.
        - Items have right spatial relationship.
    
    4. Recommended asset source priority:
        - For specific existing objects: First try Sketchfab, then PolyHaven
        - For generic objects/furniture: First try PolyHaven, then Sketchfab
        - For custom or unique items not available in libraries: Use Hyper3D Rodin
        - For environment lighting: Use PolyHaven HDRIs
        - For materials/textures: Use PolyHaven textures

    Only fall back to scripting when:
    - PolyHaven, Sketchfab, and Hyper3D are all disabled
    - A simple primitive is explicitly requested
    - No suitable asset exists in any of the libraries
    - Hyper3D Rodin failed to generate the desired asset
    - The task specifically requires a basic material/color
    """
