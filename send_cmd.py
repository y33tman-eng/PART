from pymavlink import mavutil
import time
import queue

# this function looks at the list of commands (send_queue) and then translates the command into instructions
# the plane can follow
def send_command(vehicle_connection, send_queue):
    target_system, target_component = vehicle_connection.target_system, vehicle_connection.target_component

    try:
        current_cmd = send_queue.get_nowait()
        match current_cmd[0]:
            case 'Upload Mission':
                vehicle_connection.mav.mission_count_send(target_system, target_component, len(current_cmd[1]))
            case 'Upload Mission Item':
                vehicle_connection.mav.send(current_cmd[1])
            case 'Arm Vehicle':
                vehicle_connection.mav.command_long_send(target_system, target_component,
                                                         mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0,
                                                         0, 0)
            case 'Servo Activation':
                vehicle_connection.mav.command_long_send(target_system, target_component,
                                                         mavutil.mavlink.MAV_CMD_DO_SET_SERVO, current_cmd[1],
                                                         current_cmd[2], 0, 0, 0, 0, 0)
            case 'Set Mode':
                current_mode = vehicle_connection.mode_mapping().get(current_cmd[1])
                vehicle_connection.mav.command_long_send(target_system, target_component,
                                                         mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                                                         mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                                                         current_mode, 0, 0, 0, 0, 0)
            case 'Status Text':
                message = str(current_cmd[1])
                print(message)
                vehicle_connection.mav.statustext_send(
                    mavutil.mavlink.MAV_SEVERITY_INFO,
                    message.encode())
                print('Done')
            case _:
                vehicle_connection.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_WARNING, f"ERROR".encode())
    except Exception as e:
        print(f"[ERROR] send_command failed: {e}")

if __name__ == "__main__":
    # sample send queue for testing
    vehicle_connection = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
    vehicle_connection.wait_heartbeat()

    send_queue = queue.Queue()

    # Queue some test commands
    send_queue.put(['Status Text', 'Starting test sequence'])
    send_queue.put(['Arm Vehicle'])
    send_queue.put(['Set Mode', 'GUIDED'])

    while not send_queue.empty():
        send_command(vehicle_connection, send_queue)
        time.sleep(0.5)

    print('Test Complete')