def split_string(string):
    # Split the string into lines
    lines = string.split("\n")

    # Initialize the array to store the split chunks
    split_array = []

    # Initialize the current chunk
    current_chunk = ""

    # Loop through the lines and split them into 2000-line chunks
    for line in lines:
        if len(current_chunk + line) > 2000:
            # Add the current chunk to the split array and start a new chunk
            split_array.append(current_chunk.strip())
            current_chunk = line + "\n"
        else:
            # Add the line to the current chunk
            current_chunk += line + "\n"

    # Add the last chunk to the split array
    split_array.append(current_chunk.strip())

    
    return split_array