import socket
import sys
import utils

SEPARATOR = "<SEPARATOR>"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
num_of_users_per_identifier = {}  # here we store the changes to apply for each pc num
if len(sys.argv) != 2:  # if we receive an invalid arguments we exit
    exit(-1)
portNum = int(sys.argv[1])
server.bind(('', portNum))
server.listen(5)
while True:
    client_socket, client_address = server.accept()
    data = client_socket.recv(130)  # we receive an identifier from the client at first
    identifier = data.decode('utf8')
    client_socket.send(b'pc num?')
    pc_num = client_socket.recv(100).decode('utf8')  # then we receive a pc num for identification
    # if there is no identifier we get the hello... message
    if identifier == "Hello, i am new here":
        # we create a random identifier and sending it to the client
        client_socket.send(b'1')    # sending the number of pc
        identifier = utils.create_identifier()  # we create a random identifier
        client_socket.recv(100)
        num_of_users_per_identifier[identifier] = {1: []}  # this is a new identifier so we create the first dic
        client_socket.send(identifier.encode())  # sending the identifier
        path = utils.create_new_client(identifier)  # then we create the file with the name of the identifier
        utils.recv_file(client_socket, path)  # receiving the entire folder to the identifier folder

    else:  # if we receive an identifier
        number_of_users = num_of_users_per_identifier.get(identifier)  # checking if we have the identifier in server
        if number_of_users is None:  # if not
            client_socket.send(b'1')  # sending the number of pc
            client_socket.recv(100)
            client_socket.send(b'not found')
            num_of_users_per_identifier[identifier] = {1: []}
            path = utils.create_new_client(identifier)  # then we create the file with the name of the identifier
            utils.recv_file(client_socket, path)  # receiving the entire folder to the identifier folder
        else:       # if the identifier was found

            if int(pc_num) == 0:  # if we encounter a new user
                number_of_users = sorted(num_of_users_per_identifier[identifier].keys())[-1]  # getting the last pc num
                number_of_users += 1  # adding 1 to the last pc num
                num_of_users_per_identifier[identifier][number_of_users] = []  # creating a new dict for him
                client_socket.send(str(number_of_users).encode())  # sending the pc num to client
                client_socket.recv(100)
                client_socket.send(b'found you, new')
                utils.send_all(identifier, client_socket)  # sending all of the folder to client

            else:  # if we encounter an existing client
                client_socket.send(b'found you!')
                changed_things = utils.update_file(client_socket, identifier)  # updating the file according to changes
                curr_dict = num_of_users_per_identifier[identifier]  # getting the current pc nums of identifier
                utils.updating_the_changes_to_all_users(curr_dict, int(pc_num), changed_things)  # updating users
                is_updated = utils.updating_current_user(curr_dict, int(pc_num), identifier, client_socket)
                client_socket.send(b'I have finished')
                if is_updated is True:
                    curr_dict[int(pc_num)].clear()  # if we update the current client we clear the updates
    client_socket.close()
