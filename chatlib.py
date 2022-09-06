# Protocol Constants

CMD_FIELD_LENGTH = 16	# Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10**LENGTH_FIELD_LENGTH-1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages 
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
"login_msg" : "LOGIN",
"logout_msg" : "LOGOUT",
"get_score" : "MY_SCORE",
"get_high" : "HIGHSCORE",
"logged_users" : "LOGGED",
"get_question" : "GET_QUESTION",
"send_answer" : "SEND_ANSWER",
} # .. Add more commands if needed


PROTOCOL_SERVER = {
"login_ok_msg" : "LOGIN_OK",
"login_failed_msg" : "ERROR",
"send_score" : "YOUR_SCORE",
"send_high" : "ALL_SCORE",
"logged_users" : "LOGGED_ANSWER",
"send_question" : "YOUR_QUESTION",
"no_questions" : "NO_QUESTIONS",
"correct" : "CORRECT_ANSWER",
"incorrect" : "WRONG_ANSWER"
} # ..  Add more commands if needed


# Other constants

ERROR_RETURN = None  # returned in case of an error


def build_message(cmd, data):
	"""
	Gets command name (str) and data field (str) and creates a valid protocol message
	Returns: str, or None if error occured
	"""
	try:
		data = str(data)
		if type(cmd) != str:
			raise Exception
		if cmd not in PROTOCOL_CLIENT.values() and cmd not in PROTOCOL_SERVER.values():
			return None
		elif len(data) > MAX_DATA_LENGTH:
			return None
		full_msg = f'{cmd + " " * (CMD_FIELD_LENGTH - len(cmd))}{DELIMITER}{str(0) * (LENGTH_FIELD_LENGTH - len(str(len(data))))}{len(data)}{DELIMITER}{data}'
		return full_msg
	except Exception:
		print(f"Wrong parameter input: {cmd} or {data}")


def parse_message(data):
	"""
	Parses protocol message and returns command name and data field
	Returns: cmd (str), data (str). If some error occured, returns None, None
	"""
	# try:
	if type(data) != str:
		raise Exception
	elif len(data) > MAX_MSG_LENGTH:
		return (None, None)
	cnt_delimiter = data.count(DELIMITER)
	if cnt_delimiter != 2:
		return (None, None)
	for delim in range(cnt_delimiter):
		delim_index = data.index(DELIMITER)
		field = data[:delim_index]
		if delim == 0:
			cmd = field.strip()
			if cmd not in PROTOCOL_CLIENT.values() and cmd not in PROTOCOL_SERVER.values():
				return (None, None)
			data = data[delim_index + 1:]
		elif delim == 1:
			data_len = field[:delim_index].strip()
			if not data_len.isnumeric():
				return (None, None)
			msg = data[delim_index + 1:]
			# strp_msg = data_len.strip()
			if cmd not in PROTOCOL_SERVER.values() and cmd not in PROTOCOL_CLIENT.values():
				print(cmd)
				strp_msg_len = data_len.lstrip("0")
				if len(msg) != int(strp_msg_len):
					return (None, None)
	return (cmd, msg)
	# except:
	# print(f"Wrong parameter input: {data}")

	
def split_data(msg, expected_fields):
	"""
	Helper method. gets a string and number of expected fields in it. Splits the string 
	using protocol's data field delimiter (|#) and validates that there are correct number of fields.
	Returns: list of fields if all ok. If some error occured, returns None
	"""
	list_of_strings = []
	try:
		if type(expected_fields) != int or type(msg) != str:
			raise Exception
		else:
			cnt_delimiter = msg.count(DATA_DELIMITER)
			if cnt_delimiter != expected_fields:
				return [ERROR_RETURN]
			else:
				for delim in range(cnt_delimiter):
					delim_index = msg.index(DATA_DELIMITER)
					list_of_strings.append(msg[:delim_index])
					if delim == cnt_delimiter - 1:
						list_of_strings.append(msg[delim_index + 1:])
					else:
						msg = msg[delim_index + 1:]
				return list_of_strings
	except:
		print("Wrong parameter input!")

		
def join_data(msg_fields):
	"""
	Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter. 
	Returns: string that looks like cell1#cell2#cell3
	"""
	try:
		if type(msg_fields) != list:
			raise Exception
		final_str = DATA_DELIMITER.join(msg_fields)
		if len(final_str) > MAX_DATA_LENGTH:
			return [None]
		return final_str
	except:
		print("Wrong parameter input!")