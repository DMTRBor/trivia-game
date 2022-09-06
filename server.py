##############################################################################
# server.py
##############################################################################

import socket
import chatlib
import select
import random

# GLOBALS
users = {}
questions = {}
logged_users = {} # a dictionary of client hostnames to usernames
messages_to_send = []

ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Parameters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    msg = chatlib.build_message(code, msg)
    messages_to_send.append((conn, msg))
    if code == chatlib.PROTOCOL_CLIENT["logout_msg"]:
        print("Goodbye!")

def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket,
    then parses the message using chatlib.
    Parameters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occured, will return None, None
    """
    full_msg = conn.recv(1024).decode()
    cmd, data = chatlib.parse_message(full_msg)
    print("[CLIENT] ",full_msg)	  # Debug print
    return cmd, data

def print_client_sockets(client_sockets):
    # global logged_users
    print("Connected users:")
    for c in client_sockets:
        print("\t", c.getpeername())


# Data Loaders #

def create_random_question():
    questions_db = load_questions()
    random_id = random.choice(list(questions_db.keys()))
    answers = chatlib.join_data(questions_db[random_id]["answers"])
    msg_data = chatlib.join_data([str(random_id), questions_db[random_id]["question"], answers])

    return msg_data

def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """
    questions = {
                2313 : {"question":"How much is 2+2","answers":["3","4","2","1"],"correct":2},
                4122 : {"question":"What is the capital of France","answers":["Lyon","Marseille","Paris","Montpellier"],"correct":3}
                }

    return questions

def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    users = {
            "test"		:	{"password":"test","score":0,"questions_asked":[]},
            "yossi"		:	{"password":"123","score":50,"questions_asked":[]},
            "master"	:	{"password":"master","score":200,"questions_asked":[]}
            }
    return users


# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: -
    Returns: the socket object
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen()
    return sock


def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], error_msg)


##### MESSAGE HANDLING

def handle_answer_message(conn, username, answer):
    global users

    qst_ans = load_questions()
    id_ans = chatlib.split_data(answer, 1)
    correct = qst_ans[int(id_ans[0])]['correct']
    if int(id_ans[1]) == correct:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["correct"], "YES!!!")
        users[username]['score'] += 5
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["incorrect"], f"Nope, correct answer is #{correct}")


def handle_question_message(conn):
    question = create_random_question()
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["send_question"], question)


def handle_getscore_message(conn, username):
    global users

    score = users[username]['score']
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["send_score"], score)


def handle_highscore_message(conn):
    global users

    all_scores = {}
    scores = sorted([users[user]["score"] for user in users.keys()], reverse=True)
    for score in scores:
        for user in users.keys():
            if score == users[user]["score"]:
                all_scores[user] = score
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["send_high"], all_scores)


def handle_logged_message(conn):
    global logged_users

    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["logged_users"], logged_users)


def handle_logout_message(conn):
    """
    Closes the given socket
    Recieves: socket
    Returns: None
    """
    global logged_users

    for usr, sock in logged_users.items():
         if conn == sock:
             del logged_users[usr]

    conn.close()


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users

    login_params = chatlib.split_data(data, 1)
    if login_params[0] in users.keys():
        if login_params[1] in users[login_params[0]]['password']:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"], '')
            logged_users[login_params[0]] = conn
        else:
            send_error(conn, ERROR_MSG + "Password is wrong")
            client_sockets.remove(conn)
            conn.close()
    else:
        send_error(conn, ERROR_MSG + "Username doesn't exist")
        client_sockets.remove(conn)
        conn.close()


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users	 # To be used later
    global answer_trials

    if conn in logged_users.values():
        if cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
            handle_logout_message(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["get_score"]:
            for user, sock in logged_users.items():
                if conn == sock:
                    user_name = user
            handle_getscore_message(conn, user_name)
        elif cmd == chatlib.PROTOCOL_CLIENT["get_high"]:
            handle_highscore_message(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["logged_users"]:
            handle_logged_message(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["get_question"]:
            handle_question_message(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["send_answer"]:
            for user, sock in logged_users.items():
                if conn == sock:
                    user_name = user
            handle_answer_message(conn, user_name, data)
    else:
        if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
            handle_login_message(conn, data)


def main():
    # Initializes global users and questions dicionaries using load functions
    global users
    global questions
    global client_sockets
    global messages_to_send

    print("Welcome to Trivia Server!")

    sock = setup_socket()
    client_sockets = []

    while True:
        ready_to_read, ready_to_write, in_error = select.select([sock] + client_sockets, client_sockets, [])
        for current_socket in ready_to_read:
            if current_socket is sock:
                (client_socket, client_address) = current_socket.accept()
                print("New client joined!", client_address)
                client_sockets.append(client_socket)
            else:
                try:
                    cmd, data = recv_message_and_parse(current_socket)
                    handle_client_message(current_socket, cmd, data)
                    for message in messages_to_send:
                        current_socket, data = message
                        if current_socket in ready_to_write:
                            current_socket.send(data.encode())
                            print("[SERVER] ",data)
                            messages_to_send.remove(message)
                except Exception:
                    client_sockets.remove(current_socket)
                    current_socket.close()
                    print("Client socket closed!")
                    print_client_sockets(client_sockets)


if __name__ == '__main__':
    users = load_user_database()
    main()