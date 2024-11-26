"""
https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/Mach/Mach.html

Notes:
- Forking:
 - We use fork to create a child process. This simulates two separate processes communicating via Mach ports.
- Error Handling:
 - Basic error handling is included to check the return values of Mach functions.
- Permissions:
 - Running this script does not require special permissions as it operates within user space.
- Limitations:
 - This is a simplified example. In real-world scenarios, more robust error checking and message handling would be
   necessary.
 - Mach messaging can be complex, especially with larger messages or different message types.
"""

import ctypes
import ctypes.util
import sys
from ctypes import byref
from ctypes import c_char
from ctypes import c_uint32
from ctypes import sizeof


# Load necessary libraries
libSystem = ctypes.CDLL('/usr/lib/libSystem.dylib')

# Mach types
mach_port_t = c_uint32
mach_msg_return_t = c_uint32
mach_msg_id_t = c_uint32
mach_msg_size_t = c_uint32
mach_msg_bits_t = c_uint32
mach_msg_option_t = c_uint32
mach_msg_type_number_t = c_uint32
kern_return_t = c_uint32

# Constants
MACH_PORT_NULL = 0
MACH_MSG_TYPE_MAKE_SEND = 20
MACH_PORT_RIGHT_RECEIVE = 1
MACH_MSG_TIMEOUT_NONE = 0
MACH_MSG_SUCCESS = 0x00000000
MACH_RCV_MSG = 0x00000002
MACH_SEND_MSG = 0x00000001
MACH_SEND_INVALID_DEST = 0x10000003


# Define mach_msg_header_t
class mach_msg_header_t(ctypes.Structure):
    _fields_ = [
        ('msgh_bits', mach_msg_bits_t),
        ('msgh_size', mach_msg_size_t),
        ('msgh_remote_port', mach_port_t),
        ('msgh_local_port', mach_port_t),
        ('msgh_reserved', c_uint32),
        ('msgh_id', mach_msg_id_t),
    ]


# Define mach_msg_body_t
class mach_msg_body_t(ctypes.Structure):
    _fields_ = [
        ('msgh_descriptor_count', mach_msg_size_t),
    ]


# Define the message structure
class SimpleMessage(ctypes.Structure):
    _fields_ = [
        ('header', mach_msg_header_t),
        ('body', mach_msg_body_t),
        ('data', c_char * 256),
    ]


# Function definitions
mach_task_self = ctypes.c_uint32.in_dll(libSystem, "mach_task_self_")

libSystem.mach_port_allocate.argtypes = [
    mach_port_t,
    c_uint32,
    ctypes.POINTER(mach_port_t),
]
libSystem.mach_port_allocate.restype = kern_return_t

libSystem.mach_msg.argtypes = [
    ctypes.POINTER(mach_msg_header_t),
    mach_msg_option_t,
    mach_msg_size_t,
    mach_msg_size_t,
    mach_port_t,
    mach_msg_timeout_t := c_uint32,
    mach_port_t,
]
libSystem.mach_msg.restype = mach_msg_return_t

libSystem.mach_port_insert_right.argtypes = [mach_port_t, mach_port_t, mach_port_t, c_uint32]
libSystem.mach_port_insert_right.restype = kern_return_t


def create_mach_port():
    """Allocate a Mach port."""
    my_port = mach_port_t()
    task_self = mach_task_self.value
    print(f'Self task: {task_self}')
    kr = libSystem.mach_port_allocate(task_self, MACH_PORT_RIGHT_RECEIVE, byref(my_port))
    if kr != 0:
        print('Error allocating mach port')
        sys.exit(1)
    # Insert a send right into the port
    kr = libSystem.mach_port_insert_right(mach_task_self.value, my_port, my_port, MACH_MSG_TYPE_MAKE_SEND)
    if kr != 0:
        print(f"Error inserting send right: {kr}")
        sys.exit(1)
    return my_port


def send_message(remote_port, message_text):
    """Send a message to the specified Mach port."""
    print(f"Sending message to port: {remote_port.value}")

    message = SimpleMessage()
    message.header.msgh_bits = MACH_MSG_TYPE_MAKE_SEND
    message.header.msgh_size = sizeof(SimpleMessage)
    message.header.msgh_remote_port = remote_port
    message.header.msgh_local_port = MACH_PORT_NULL
    message.header.msgh_reserved = 0
    message.header.msgh_id = 100  # Message ID can be any arbitrary number

    # Copy the message text
    ctypes.memset(message.data, 0, 256)
    ctypes.memmove(message.data, message_text.encode('utf-8'), len(message_text))

    ret = libSystem.mach_msg(
        byref(message.header),
        MACH_SEND_MSG,
        message.header.msgh_size,
        0,
        MACH_PORT_NULL,
        MACH_MSG_TIMEOUT_NONE,
        MACH_PORT_NULL,
    )
    if ret != MACH_MSG_SUCCESS:
        print(f'Error sending message: {ret}')
        sys.exit(1)
    else:
        print('Message sent successfully.')


def receive_message(local_port):
    """Receive a message from the specified Mach port."""
    message = SimpleMessage()
    message.header.msgh_local_port = local_port

    ret = libSystem.mach_msg(
        byref(message.header),
        MACH_RCV_MSG,
        0,
        sizeof(SimpleMessage),
        local_port,
        MACH_MSG_TIMEOUT_NONE,
        MACH_PORT_NULL,
    )
    if ret != MACH_MSG_SUCCESS:
        print(f'Error receiving message: {ret}')
        sys.exit(1)
    else:
        print('Message received successfully.')
        received_text = message.data.value.decode('utf-8')
        print(f'Received message: {received_text}')


def main():
    # Create a Mach port
    my_port = create_mach_port()
    print(f'Created Mach port: {my_port.value}')

    # Fork the process to simulate IPC
    pid = libSystem.fork()
    if pid == 0:
        # Child process: send a message
        send_message(my_port, 'Hello from child process!')
        sys.exit(0)
    else:
        # Parent process: receive the message
        receive_message(my_port)


if __name__ == '__main__':
    main()
