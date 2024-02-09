MAX_MESSAGE_LEN = 2000


def split_message_to_chunks(text):
    lines = text.splitlines(True)
    msg_chunks = []

    curr_msg_chunk = ""

    curr_code_block = ""
    is_code_block = False

    for line in lines:
        if line.lstrip().startswith("```"):
            is_code_block = not is_code_block

            if is_code_block:
                curr_code_block += "\n"

            if not is_code_block:
                curr_code_block += line

                if len(curr_msg_chunk + curr_code_block) < MAX_MESSAGE_LEN:
                    curr_msg_chunk += curr_code_block
                else:
                    msg_chunks.append(curr_msg_chunk)
                    curr_msg_chunk = curr_code_block

                curr_code_block = ""
                continue

        if is_code_block:
            curr_code_block += line
            continue

        # normal ones
        if len(curr_msg_chunk + line) < MAX_MESSAGE_LEN:
            curr_msg_chunk += line.lstrip()
        else:
            msg_chunks.append(curr_msg_chunk)
            curr_msg_chunk = line.lstrip()

    # handle last chunk
    if curr_msg_chunk:
        msg_chunks.append(curr_msg_chunk)
    if curr_code_block:
        msg_chunks.append(curr_code_block)

    return msg_chunks
