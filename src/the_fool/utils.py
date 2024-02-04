MAX_MESSAGE_LEN = 2000


def split_message_to_chunks(text):
    paragraphs = text.splitlines()
    msg_chunks = []

    curr_msg_chunk = ""
    for paragraph in paragraphs:
        if len(curr_msg_chunk + paragraph) < MAX_MESSAGE_LEN:
            curr_msg_chunk += f"{paragraph}\n"
        else:
            msg_chunks.append(curr_msg_chunk)
            curr_msg_chunk = f"{paragraph}\n"

    # last chunk
    msg_chunks.append(curr_msg_chunk)

    return msg_chunks
