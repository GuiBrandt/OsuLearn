def read_byte(file):
    return ord(file.read(1))

def read_short(file):
    return read_byte(file) + (read_byte(file) << 8)

def read_int(file):
    return read_short(file) + (read_short(file) << 16)

def read_long(file):
    return read_int(file) + (read_int(file) << 32)

def read_uleb128(file):
    n = 0
    i = 0
    while True:
        byte = read_byte(file)
        n += (byte & 0x7F) << i
        if byte & 0x80 != 0:
            i += 7
        else:
            return n

def read_binary_string(file):
    while True:
        flag = read_byte(file)
        if flag == 0x00:
            return ""
        elif flag == 0x0b:
            length = read_uleb128(file)
            return file.read(length).decode('utf8')
        else:
            raise RuntimeError("Invalid file")