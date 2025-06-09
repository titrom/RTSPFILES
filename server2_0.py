import socket
import json

def parse_pelcod(data):
    if len(data) != 7 or data[0] != 0xFF:
        return {"error": "Invalid packet format or sync byte"}

    sync, addr, cmd1, cmd2, data1, data2, checksum = data
    calculated_checksum = sum(data[1:6]) % 256

    if calculated_checksum != checksum:
        return {
            "error": "Checksum mismatch",
            "expected": hex(calculated_checksum),
            "received": hex(checksum)
        }

    direction = "stop"
    pan_speed = 0
    tilt_speed = 0
    zoom_position_mm = None

    # --- MOVEMENT ---
    if cmd1 == 0x00 and cmd2 == 0x08:
        direction = "up"
        tilt_speed = data2
    elif cmd1 == 0x00 and cmd2 == 0x10:
        direction = "down"
        tilt_speed = data2
    elif cmd1 == 0x00 and cmd2 == 0x04:
        direction = "left"
        pan_speed = data1
    elif cmd1 == 0x00 and cmd2 == 0x02:
        direction = "right"
        pan_speed = data1
    elif cmd1 == 0x00 and cmd2 == 0x0C:
        direction = "upper_left"
        pan_speed = data1
        tilt_speed = data2
    elif cmd1 == 0x00 and cmd2 == 0x14:
        direction = "lower_left"
        pan_speed = data1
        tilt_speed = data2
    elif cmd1 == 0x00 and cmd2 == 0x0A:
        direction = "upper_right"
        pan_speed = data1
        tilt_speed = data2
    elif cmd1 == 0x00 and cmd2 == 0x12:
        direction = "lower_right"
        pan_speed = data1
        tilt_speed = data2
    elif cmd1 == 0x00 and cmd2 == 0x00:
        direction = "stop"
        pan_speed = 0
        tilt_speed = 0

    # --- SET ZOOM POSITION (0x4F) ---
    elif cmd1 == 0x00 and cmd2 == 0x4F:
        pelco_value = (data1 << 8) | data2
        zoom_position_mm = (pelco_value / 65535) * 240.0  # Преобразуем в мм
        return {
            "command_type": "set_zoom",
            "zoom_position_mm": zoom_position_mm
        }

    return {
        "direction": direction,
        "pan_speed": pan_speed,
        "tilt_speed": tilt_speed,
        "zoom_position": zoom_position_mm
    }

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen(1)

    print("TCP-сервер запущен на порту 9999...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Подключено: {addr}")

        try:
            data = client_socket.recv(7)
            if data:
                parsed = parse_pelcod(list(data))
                
                print(json.dumps(parsed, indent=2))

                with open('last_command.json', 'w') as f:
                    json.dump(parsed, f, indent=2)

                # Отправляем клиенту ответ
                client_socket.sendall(json.dumps(parsed).encode('utf-8'))

        finally:
            client_socket.close()

if __name__ == "__main__":
    main()