from pymavlink import mavutil
import time
import math
import threading

# defining the send_waypoints event
send_waypoints_event = threading.Event()

# this function continuously looks for messages from the vehicle and then stores them in the forwarder_queue, unless it has to be parsed beforehand.

def rec_msg(vehicle_connection, send_queue, forwarder_queue):

    while True:
        msg = vehicle_connection.recv_match(blocking= True)
        msg_type = msg.get_type()
        
        forwarder_queue.put(msg)
        
        if msg_type == 'GLOBAL_POSITION_INT':
            lat = msg.lat
            lon = msg.lon
            alt = msg.alt
            
            converted_pos = convert_pos(lat, lon, alt)
            send_pos(converted_pos)
            
        elif msg_type == 'MISSION_REQUEST_INT' or 'MISSION_REQUEST':
            # I am supposed to set and reset the send_waypoints event, i do not know what that means
            send_waypoints_event.set()
            time.sleep(1)
            send_waypoints_event.clear()
        
        elif msg_type == 'MISSION_ITEM_REACHED':
            num_waypoint = msg.seq
            vehicle_connection.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_WARNING, f"Waypoint {num_waypoint} reached".encode())
        else:
            vehicle_connection.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_WARNING, f"ERROR".encode())   
        