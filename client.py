import socket
import chatlib  # To use chatlib functions or consts, use chatlib.****

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678

# HELPER SOCKET METHODS

def build_and_send_message(conn, code, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    msg = chatlib.build_message(code, data)
    if code == chatlib.PROTOCOL_CLIENT["logout_msg"]:
        print("Goodbye!")
    conn.send(msg.encode())


def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket,
    then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occured, will return None, None
    """
    full_msg = conn.recv(1024).decode()
    cmd, data = chatlib.parse_message(full_msg)
    return cmd, data


def build_send_recv_parse(conn, cmd, data):
    build_and_send_message(conn, cmd, data)
    msg_code, data = recv_message_and_parse(conn)
    return msg_code, data


def get_score(conn):
    code, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["get_score"], '')
    if code != chatlib.PROTOCOL_SERVER["send_score"]:
        error_and_exit(f"ERROR!!!Received {code} command instead of {chatlib.PROTOCOL_SERVER['send_score']}")
    print(data)


def get_highscore(conn):
    code, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["get_high"], '')
    if code != chatlib.PROTOCOL_SERVER["send_high"]:
        error_and_exit(f"ERROR!!!Received {code} command instead of {chatlib.PROTOCOL_SERVER['send_high']}")
    print(data)

def connect():
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((SERVER_IP, SERVER_PORT))
    print(f'Connecting to {SERVER_IP} port {SERVER_PORT}')
    return conn


def error_and_exit(error_msg):
    print(error_msg)
    exit()


def login(conn):
    while True:
        username = input("Please enter username: \n")
        password = input("Please enter password: \n")
        login_str = chatlib.join_data([username, password])
        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], login_str)
        cmd, data = recv_message_and_parse(conn)
        if cmd == chatlib.PROTOCOL_SERVER["login_ok_msg"]:
            print("Logged in!")
            return
        else:
            print(data)
            exit()


def logout(conn):
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")


def get_logged_users(conn):
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["logged_users"], '')
    if cmd == chatlib.PROTOCOL_SERVER["logged_users"]:
        print(data)
    else:
        error_and_exit(f"ERROR!!!Received {cmd} command instead of {chatlib.PROTOCOL_SERVER['logged_users']}")


def play_question(conn):
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["get_question"], '')
    if cmd == chatlib.PROTOCOL_SERVER["send_question"]:
        data = chatlib.split_data(data, 5)
        data_backup = data
        print(f"Q:{data[1]}?:\n\t1.{data[2]}\n\t2.{data[3]}\n\t3.{data[4]}\n\t4.{data[5]}")
        while cmd != chatlib.PROTOCOL_SERVER["correct"]:
            answer = input("Please choose an answer [1-4]: ")
            cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["send_answer"], chatlib.join_data([data[0], answer]))
            data = data_backup
        if cmd == chatlib.PROTOCOL_SERVER["correct"] or chatlib.PROTOCOL_SERVER["incorrect"]:
            print("YES!!!")
        else:
            error_and_exit(f"Error!!!Wrong command received: {cmd}")
            return
    elif cmd == chatlib.PROTOCOL_SERVER["no_questions"]:
        print("There are no more questions remained!!!")


def main():
    socket = connect()
    login(socket)
    while True:
        try:
            print("p        Play a trivia question\ns        Get my score\nh        Get high score\nl        Get logged users\nq        Quit")
            choice = input("Please enter your choice: ")
            if choice == 'p':
                play_question(socket)
            elif choice == 's':
                get_score(socket)
            elif choice == 'h':
                get_highscore(socket)
            elif choice == 'l':
                get_logged_users(socket)
            elif choice == 'q':
                logout(socket)
                exit()
        except KeyboardInterrupt:
            logout(socket)
            exit()

if __name__ == '__main__':
    main()
