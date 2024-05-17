"""
Посмотреть название рабочей директории - pwd
Посмотреть содержимое папки - ls
Создать папку - mkdir <dirname>
Удалить папку - deldir <dirname>
Удалить файл -  rm <filename>
Переименовать файл - mv <oldname> <newname>
Скопировать файл с клиента на сервер - clienttoserver <filename> <content>
Скопировать файл с сервера на клиент - servertoclient <filename>
Выход (отключение клиента от сервера) - exit

Проверка 1 доп задания:
например, при командах:
mkdir ../outside_dir
rm ../outside_dir/file.txt
ls ../
должно выводиться:
Operation not permitted. Access outside the directory is restricted.

Проверка 2 доп задания:
Действия должны записываться в файл "server_actions.log"

Проверка 3 доп задания:
при попытке ввода команда должно выводиться "Please log in to continue."
после авторизации, то есть ввода "login admin adminpass"
должно выводиться: "You are now logged in."
и после этого можно выполнять команды
"""

import socket
import os
import shutil
import logging

logging.basicConfig(filename='server_actions.log', level=logging.INFO, format='%(asctime)s - %(message)s')

dirname = os.path.join(os.getcwd(), 'docs')


def process(req, is_authenticated):
    if not is_authenticated:
        if req.startswith('login'):
            _, username, password = req.split()
            if username == 'admin' and password == 'adminpass':
                logging.info(f'User {username} logged in successfully.')
                return 'You are now logged in.'
            else:
                logging.warning(f'Failed login attempt for {username}.')
                return 'Invalid credentials. Please try again or contact your administrator.'
        else:
            return 'Please log in to continue.'

    if req == 'pwd':
        return dirname

    if not req.startswith('pwd') and not req.startswith('exit'):
        req_split = req.split()
        if len(req_split) > 1:
            path = os.path.normpath(os.path.join(dirname, req_split[1]))
            if not os.path.commonpath([os.path.abspath(dirname), os.path.abspath(path)]) == os.path.abspath(dirname):
                return "Operation not permitted. Access outside the directory is restricted."

    if req == 'ls':
        contents = os.listdir(dirname)
        if contents:
            response = '; '.join(contents)
            logging.info(f'Listed contents of directory: {response}')
            return response
        else:
            return "No files or folders in the current directory."

    if req.startswith('mkdir'):
        dir_name = req.split()[1]
        os.mkdir(os.path.join(dirname, dir_name))
        logging.info(f'Created directory: {dir_name}')
        return f"Directory {dir_name} created successfully."

    if req.startswith('deldir'):
        dir_name = req.split()[1]
        shutil.rmtree(os.path.join(dirname, dir_name))
        logging.info(f'Deleted directory: {dir_name}')
        return f"Directory {dir_name} deleted successfully."

    if req.startswith('rm'):
        file_name = req.split()[1]
        os.remove(os.path.join(dirname, file_name))
        logging.info(f'Deleted file: {file_name}')
        return f"File {file_name} deleted successfully."

    if req.startswith('mv'):
        old_name, new_name = req.split()[1:]
        os.rename(os.path.join(dirname, old_name), os.path.join(dirname, new_name))
        logging.info(f'Renamed file: {old_name} to {new_name}')
        return f"File {old_name} renamed to {new_name} successfully."

    if req.startswith('clienttoserver'):
        _, file_name, content = req.split(maxsplit=2)
        file_path = os.path.join(dirname, file_name)
        with open(file_path, 'w') as f:
            f.write(content)
        logging.info(f'Created file on server: {file_name}')
        return f"File {file_name} created on server."

    if req.startswith('servertoclient'):
        file_name = req.split()[1]
        file_path = os.path.join(dirname, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_content = f.read()
            logging.info(f'Sent file to client: {file_name}')
            conn.send(file_content)
            return f"File {file_name} sent to client successfully."
        else:
            return f"File {file_name} does not exist on the server."

    return 'bad request'


PORT = 8080

sock = socket.socket()
sock.bind(('', PORT))
sock.listen()
print("Listening on port", PORT)

is_authenticated = False

while True:
    conn, addr = sock.accept()

    request = conn.recv(1024).decode()
    print(request)

    response = process(request, is_authenticated)

    if response == 'You are now logged in.':
        is_authenticated = True

    if response == 'exit':
        is_authenticated = False
        conn.close()
        break

    conn.send(response.encode())

conn.close()
