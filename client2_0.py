import socket
import json

# Константы
HOST = '127.0.0.1'
PORT = 9999
ZOOM_LIMIT_MM = 240.0  # Максимальное фокусное расстояние камеры (мм)

def send_to_server(packet):
    """Отправляет пакет на сервер"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.sendall(bytes(packet))
            response = s.recv(1024)
            print("Ответ от сервера:", response.decode())
            return response
        except Exception as e:
            print("Ошибка подключения к серверу:", e)

def main():
    while True:
        choice = input("Выберите команду:\n"
                      "1 — Вверх\n"
                      "2 — Вниз\n"
                      "3 — Влево\n"
                      "4 — Вправо\n"
                      "5 — Стоп движение\n"
                      "6 — Установить зум (в мм)\n"
                      "q — Выход\n"
                      "Введите номер команды или 'q': ")

        if choice == 'q':
            break

        if choice == '6':
            zoom_mm = float(input("Введите фокусное расстояние (от 6.5 до 240 мм): "))
            if not (6.5 <= zoom_mm <= 240):
                print("Ошибка: Значение должно быть между 6.5 и 240 мм")
                continue

            # Преобразование фокусного расстояния в PELCO Zoom value
            pelco_value = int((zoom_mm / ZOOM_LIMIT_MM) * 65535)
            data1 = pelco_value >> 8  # MSB
            data2 = pelco_value & 0xFF  # LSB

            packet = [0xFF, 0x01, 0x00, 0x4F, data1, data2, 0x00]
            packet[-1] = sum(packet[1:6]) % 256  # Вычисляем контрольную сумму
            send_to_server(packet)

if __name__ == "__main__":
    main()