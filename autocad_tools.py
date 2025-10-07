from pyautocad import Autocad, APoint
import math
import pythoncom
from typing import List, Dict, Any, Optional, Union


METERS_TO_UNITS = 1000 


entity_groups = {}
current_group_id = 0

def get_next_group_id() -> str:
    """Get next group ID for tracking entities"""
    global current_group_id
    current_group_id += 1
    return f"group_{current_group_id}"

def clear_all_entities() -> dict:
    """Clear all entities and reset group tracking"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        
        model_space = acad.doc.ModelSpace
        count = 0
        entities = [entity for entity in model_space]
        
        for entity in entities:
            try:
                entity.Delete()
                count += 1
            except Exception as e:
                print(f"⚠ Couldn't delete entity: {e}")
        
        
        global entity_groups, current_group_id
        entity_groups = {}
        current_group_id = 0
        
        
        try:
            acad.doc.SendCommand("ZOOM E\n")
        except:
            pass
        
        return {
            "success": True,
            "message": f"Cleared {count} entities and reset groups",
            "count": count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}



def delete_group(group_name: str) -> dict:
    """Delete all entities in a specific group"""
    try:
        if group_name not in entity_groups:
            return {
                "success": False,
                "message": f"Group '{group_name}' not found",
                "available_groups": list(entity_groups.keys())
            }
        
        count = 0
        entities = entity_groups[group_name]
        
        for entity in entities:
            try:
                entity.Delete()
                count += 1
            except Exception as e:
                print(f"Couldn't delete entity: {e}")
        
        # Remove group from tracking
        del entity_groups[group_name]
        
        return {
            "success": True,
            "message": f" Deleted group '{group_name}' with {count} entities",
            "count": count
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_groups() -> dict:
    """List all available entity groups"""
    return {
        "success": True,
        "groups": list(entity_groups.keys()),
        "total_groups": len(entity_groups)
    }

def draw_rectangle_simple(x1: float, y1: float, x2: float, y2: float, 
                         group_name: str = None) -> dict:
    """Draw a simple rectangle outline"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        
        x1_u = x1 * METERS_TO_UNITS
        y1_u = y1 * METERS_TO_UNITS
        x2_u = x2 * METERS_TO_UNITS
        y2_u = y2 * METERS_TO_UNITS
        
        # Draw 4 lines
        lines = []
        points = [
            (x1_u, y1_u), (x2_u, y1_u),
            (x2_u, y1_u), (x2_u, y2_u),
            (x2_u, y2_u), (x1_u, y2_u),
            (x1_u, y2_u), (x1_u, y1_u) 
        ]
        
        for i in range(0, len(points), 2):
            p1 = APoint(points[i][0], points[i][1])
            p2 = APoint(points[i+1][0], points[i+1][1])
            line = acad.model.AddLine(p1, p2)
            lines.append(line)
        
        if not group_name:
            group_name = get_next_group_id()
        
        if group_name not in entity_groups:
            entity_groups[group_name] = []
        
        entity_groups[group_name].extend(lines)
        
        return {
            "success": True,
            "message": "Rectangle drawn",
            "group_name": group_name,
            "corners_m": [[x1, y1], [x2, y2]],
            "lines_count": len(lines)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def draw_circle_simple(x: float, y: float, radius: float, group_name: str = None) -> dict:
    """Draw a simple circle"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        
        center = APoint(x * METERS_TO_UNITS, y * METERS_TO_UNITS)
        radius_u = radius * METERS_TO_UNITS
        circle = acad.model.AddCircle(center, radius_u)
        
        # Track in group
        if not group_name:
            group_name = get_next_group_id()
        
        if group_name not in entity_groups:
            entity_groups[group_name] = []
        
        entity_groups[group_name].append(circle)
        
        return {
            "success": True,
            "message": "Circle drawn",
            "group_name": group_name,
            "center_m": [x, y],
            "radius_m": radius
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def draw_line_simple(x1: float, y1: float, x2: float, y2: float, 
                    group_name: str = None) -> dict:
    """Draw a simple line"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        
        p1 = APoint(x1 * METERS_TO_UNITS, y1 * METERS_TO_UNITS)
        p2 = APoint(x2 * METERS_TO_UNITS, y2 * METERS_TO_UNITS)
        line = acad.model.AddLine(p1, p2)
        
        
        if not group_name:
            group_name = get_next_group_id()
        
        if group_name not in entity_groups:
            entity_groups[group_name] = []
        
        entity_groups[group_name].append(line)
        
        return {
            "success": True,
            "message": "Line drawn",
            "group_name": group_name,
            "start_m": [x1, y1],
            "end_m": [x2, y2]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def draw_line_by_angle(x: float, y: float, length_m: float, angle_deg: float, 
                      group_name: str = None) -> dict:
    """Draw a line from a point with given length and angle"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        
        angle_rad = math.radians(angle_deg)
        x1 = x * METERS_TO_UNITS
        y1 = y * METERS_TO_UNITS
        length = length_m * METERS_TO_UNITS
        x2 = x1 + length * math.cos(angle_rad)
        y2 = y1 + length * math.sin(angle_rad)
        
        p1 = APoint(x1, y1)
        p2 = APoint(x2, y2)
        line = acad.model.AddLine(p1, p2)
        
        # Track in group
        if not group_name:
            group_name = get_next_group_id()
        
        if group_name not in entity_groups:
            entity_groups[group_name] = []
        
        entity_groups[group_name].append(line)
        
        return {
            "success": True,
            "message": "Line drawn by angle",
            "group_name": group_name,
            "start_m": [x, y],
            "length_m": length_m,
            "angle_deg": angle_deg
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def zoom_extents() -> dict:
    """Zoom to show all entities in the drawing"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        acad.doc.SendCommand("ZOOM E\n")
        
        return {
            "success": True,
            "message": "Zoomed to extents"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def move_group(group_name: str, dx: float, dy: float) -> dict:
    """Move all entities in a group"""
    try:
        if group_name not in entity_groups:
            return {
                "success": False,
                "message": f"Group '{group_name}' not found"
            }
        
        pythoncom.CoInitialize()
        move_vector = APoint(dx * METERS_TO_UNITS, dy * METERS_TO_UNITS)
        count = 0
        
        for entity in entity_groups[group_name]:
            try:
                entity.Move(APoint(0, 0), move_vector)
                count += 1
            except Exception as e:
                print(f"⚠ Couldn't move entity: {e}")
        
        return {
            "success": True,
            "message": f"✅ Moved {count} entities in group '{group_name}'",
            "count": count,
            "offset_m": [dx, dy]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def copy_group(group_name: str, dx: float, dy: float, new_group_name: str = None) -> dict:
    """Copy all entities in a group to a new location"""
    try:
        if group_name not in entity_groups:
            return {
                "success": False,
                "message": f"Group '{group_name}' not found"
            }
        
        pythoncom.CoInitialize()
        copy_vector = APoint(dx * METERS_TO_UNITS, dy * METERS_TO_UNITS)
        
        if not new_group_name:
            new_group_name = f"{group_name}_copy_{get_next_group_id()}"
        
        new_entities = []
        count = 0
        
        for entity in entity_groups[group_name]:
            try:
                copied = entity.Copy()
                copied.Move(APoint(0, 0), copy_vector)
                new_entities.append(copied)
                count += 1
            except Exception as e:
                print(f"⚠ Couldn't copy entity: {e}")
        
        # Track new group
        entity_groups[new_group_name] = new_entities
        
        return {
            "success": True,
            "message": f"✅ Copied {count} entities to new group '{new_group_name}'",
            "original_group": group_name,
            "new_group": new_group_name,
            "count": count,
            "offset_m": [dx, dy]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def rotate_group(group_name: str, base_x: float, base_y: float, angle_deg: float) -> dict:
    """Rotate all entities in a group around a base point"""
    try:
        if group_name not in entity_groups:
            return {
                "success": False,
                "message": f"Group '{group_name}' not found"
            }
        
        pythoncom.CoInitialize()
        base_point = APoint(base_x * METERS_TO_UNITS, base_y * METERS_TO_UNITS)
        angle_rad = math.radians(angle_deg)
        count = 0
        
        for entity in entity_groups[group_name]:
            try:
                entity.Rotate(base_point, angle_rad)
                count += 1
            except Exception as e:
                print(f"⚠ Couldn't rotate entity: {e}")
        
        return {
            "success": True,
            "message": f"✅ Rotated {count} entities in group '{group_name}'",
            "count": count,
            "base_point_m": [base_x, base_y],
            "angle_deg": angle_deg
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def scale_group(group_name: str, base_x: float, base_y: float, scale_factor: float) -> dict:
    """Scale all entities in a group from a base point"""
    try:
        if group_name not in entity_groups:
            return {
                "success": False,
                "message": f"Group '{group_name}' not found"
            }
        
        pythoncom.CoInitialize()
        base_point = APoint(base_x * METERS_TO_UNITS, base_y * METERS_TO_UNITS)
        count = 0
        
        for entity in entity_groups[group_name]:
            try:
                entity.ScaleEntity(base_point, scale_factor)
                count += 1
            except Exception as e:
                print(f"⚠ Couldn't scale entity: {e}")
        
        return {
            "success": True,
            "message": f"✅ Scaled {count} entities in group '{group_name}'",
            "count": count,
            "base_point_m": [base_x, base_y],
            "scale_factor": scale_factor
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def mirror_group(group_name: str, mirror_x1: float, mirror_y1: float, 
                mirror_x2: float, mirror_y2: float, keep_original: bool = True) -> dict:
    """Mirror all entities in a group across a line"""
    try:
        if group_name not in entity_groups:
            return {
                "success": False,
                "message": f"Group '{group_name}' not found"
            }
        
        pythoncom.CoInitialize()
        mirror_pt1 = APoint(mirror_x1 * METERS_TO_UNITS, mirror_y1 * METERS_TO_UNITS)
        mirror_pt2 = APoint(mirror_x2 * METERS_TO_UNITS, mirror_y2 * METERS_TO_UNITS)
        
        new_group_name = f"{group_name}_mirrored_{get_next_group_id()}"
        new_entities = []
        count = 0
        
        for entity in entity_groups[group_name]:
            try:
                mirrored = entity.Mirror(mirror_pt1, mirror_pt2)
                new_entities.append(mirrored)
                count += 1
            except Exception as e:
                print(f"⚠ Couldn't mirror entity: {e}")
        
        # Track new group
        entity_groups[new_group_name] = new_entities
        
        # Delete originals if requested
        if not keep_original:
            delete_group(group_name)
        
        return {
            "success": True,
            "message": f"✅ Mirrored {count} entities to new group '{new_group_name}'",
            "original_group": group_name,
            "new_group": new_group_name,
            "count": count,
            "mirror_line": [[mirror_x1, mirror_y1], [mirror_x2, mirror_y2]],
            "kept_original": keep_original
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def draw_polyline(points: List[Union[List[float], Dict[str, float]]], closed: bool = False, group_name: str = None) -> dict:
    """Draw a polyline through multiple points.

    Accepts points either as [[x,y], ...] or as [{"x": x, "y": y}, ...] to better align with
    structured tool calling constraints (avoids nested array-of-array schema issues)."""
    try:
        norm_points: List[List[float]] = []
        for p in points:
            if isinstance(p, dict):
                norm_points.append([float(p.get("x")), float(p.get("y"))])
            else:
                norm_points.append([float(p[0]), float(p[1])])
        if len(norm_points) < 2:
            return {"success": False, "error": "Need at least 2 points for polyline"}

        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)

        autocad_points = []
        for x_val, y_val in norm_points:
            autocad_points.extend([x_val * METERS_TO_UNITS, y_val * METERS_TO_UNITS])

        if closed:
            autocad_points.extend([norm_points[0][0] * METERS_TO_UNITS, norm_points[0][1] * METERS_TO_UNITS])

        polyline = acad.model.AddLightWeightPolyline(autocad_points)
        polyline.Closed = closed

        if not group_name:
            group_name = get_next_group_id()
        if group_name not in entity_groups:
            entity_groups[group_name] = []
        entity_groups[group_name].append(polyline)

        return {
            "success": True,
            "message": "Polyline drawn",
            "group_name": group_name,
            "points_m": norm_points,
            "closed": closed,
            "point_count": len(norm_points)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def draw_arc(center_x: float, center_y: float, radius: float, 
            start_angle_deg: float, end_angle_deg: float, group_name: str = None) -> dict:
    """Draw an arc"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        
        center = APoint(center_x * METERS_TO_UNITS, center_y * METERS_TO_UNITS)
        radius_u = radius * METERS_TO_UNITS
        start_angle_rad = math.radians(start_angle_deg)
        end_angle_rad = math.radians(end_angle_deg)
        
        arc = acad.model.AddArc(center, radius_u, start_angle_rad, end_angle_rad)
        
        # Track in group
        if not group_name:
            group_name = get_next_group_id()
        
        if group_name not in entity_groups:
            entity_groups[group_name] = []
        
        entity_groups[group_name].append(arc)
        
        return {
            "success": True,
            "message": "Arc drawn",
            "group_name": group_name,
            "center_m": [center_x, center_y],
            "radius_m": radius,
            "start_angle_deg": start_angle_deg,
            "end_angle_deg": end_angle_deg
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def draw_text(x: float, y: float, text: str, height: float = 0.2, 
             angle_deg: float = 0, group_name: str = None) -> dict:
    """Draw text at specified position"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        
        insertion_point = APoint(x * METERS_TO_UNITS, y * METERS_TO_UNITS)
        height_u = height * METERS_TO_UNITS
        angle_rad = math.radians(angle_deg)
        
        text_obj = acad.model.AddText(text, insertion_point, height_u)
        text_obj.Rotation = angle_rad
        
        # Track in group
        if not group_name:
            group_name = get_next_group_id()
        
        if group_name not in entity_groups:
            entity_groups[group_name] = []
        
        entity_groups[group_name].append(text_obj)
        
        return {
            "success": True,
            "message": "Text drawn",
            "group_name": group_name,
            "position_m": [x, y],
            "text": text,
            "height_m": height,
            "angle_deg": angle_deg
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def draw_dimension_linear(x1: float, y1: float, x2: float, y2: float,
                         dim_line_y: float, group_name: str = None) -> dict:
    """Draw a linear dimension between two points"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        
        pt1 = APoint(x1 * METERS_TO_UNITS, y1 * METERS_TO_UNITS)
        pt2 = APoint(x2 * METERS_TO_UNITS, y2 * METERS_TO_UNITS)
        dim_line_pt = APoint((x1 + x2) / 2 * METERS_TO_UNITS, dim_line_y * METERS_TO_UNITS)
        
        dimension = acad.model.AddDimAligned(pt1, pt2, dim_line_pt)
        
        # Track in group
        if not group_name:
            group_name = get_next_group_id()
        
        if group_name not in entity_groups:
            entity_groups[group_name] = []
        
        entity_groups[group_name].append(dimension)
        
        return {
            "success": True,
            "message": "Linear dimension drawn",
            "group_name": group_name,
            "start_m": [x1, y1],
            "end_m": [x2, y2],
            "dim_line_y_m": dim_line_y
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def set_layer(layer_name: str, color: int = 7) -> dict:
    """Create or set current layer"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        
        # Try to get existing layer, create if doesn't exist
        try:
            layer = acad.doc.Layers.Item(layer_name)
        except:
            layer = acad.doc.Layers.Add(layer_name)
            layer.color = color
        
        # Set as current layer
        acad.doc.ActiveLayer = layer
        
        return {
            "success": True,
            "message": f"Layer '{layer_name}' set as current",
            "layer_name": layer_name,
            "color": color
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_drawing_extents() -> dict:
    """Get the extents of the current drawing"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        
        model_space = acad.doc.ModelSpace
        entity_count = len([e for e in model_space])
        
        if entity_count == 0:
            return {
                "success": True,
                "message": "No entities in drawing",
                "entity_count": 0,
                "extents_m": None
            }
        
        # Get drawing extents
        extents = acad.doc.GetVariable("EXTMIN"), acad.doc.GetVariable("EXTMAX")
        
        min_point = [extents[0][0] / METERS_TO_UNITS, extents[0][1] / METERS_TO_UNITS]
        max_point = [extents[1][0] / METERS_TO_UNITS, extents[1][1] / METERS_TO_UNITS]
        
        return {
            "success": True,
            "message": "Drawing extents retrieved",
            "entity_count": entity_count,
            "extents_m": {
                "min": min_point,
                "max": max_point,
                "width": max_point[0] - min_point[0],
                "height": max_point[1] - min_point[1]
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Legacy functions for backward compatibility
def draw_rectangle(x1: float, y1: float, x2: float, y2: float) -> dict:
    """Legacy function - use draw_rectangle_simple instead"""
    return draw_rectangle_simple(x1, y1, x2, y2)

def draw_circle(x: float, y: float, radius_m: float) -> dict:
    """Legacy function - use draw_circle_simple instead"""
    return draw_circle_simple(x, y, radius_m)

def erase_all() -> dict:
    """Legacy function - use clear_all_entities instead"""
    return clear_all_entities()

def erase_selected_by_shape(shape: str) -> dict:
    """Legacy function - groups provide better control"""
    return {
        "success": False,
        "message": "Use group-based functions instead. This function deleted too many entities.",
        "suggestion": "Use delete_group() or clear_all_entities()"
    }

def move_all(dx: float, dy: float) -> dict:
    """Move all entities (legacy function)"""
    try:
        pythoncom.CoInitialize()
        acad = Autocad(create_if_not_exists=True)
        
        model_space = acad.doc.ModelSpace
        move_vector = APoint(dx * METERS_TO_UNITS, dy * METERS_TO_UNITS)
        count = 0
        
        entities = [entity for entity in model_space]
        
        for entity in entities:
            try:
                entity.Move(APoint(0, 0), move_vector)
                count += 1
            except Exception as e:
                print(f"⚠ Couldn't move entity: {e}")
        
        return {
            "success": True,
            "message": f"✅ Moved {count} entities by [{dx}m, {dy}m]",
            "count": count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    

tools = [move_all,erase_selected_by_shape,erase_all,draw_circle,draw_rectangle,get_drawing_extents,set_layer,draw_dimension_linear,draw_text,draw_arc,draw_polyline,mirror_group,scale_group,rotate_group,get_next_group_id,clear_all_entities,delete_group,list_groups,draw_rectangle_simple,draw_circle_simple,draw_line_simple,draw_line_by_angle,zoom_extents,move_group,copy_group]