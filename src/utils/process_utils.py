from ctypes import cdll, byref, create_string_buffer


def set_proc_name(procname: str) -> None:
    """Sets the process name in Linux \n
    
    This only works for a maximum of 16 bytes (including the null termination), 
    if the input is longer it will get truncated
    
    Args:
        procname (str): Process name to be used
    """
    byte_procname = procname.encode("utf-8")

    # Buffer to hold the new process name
    libc = cdll.LoadLibrary("libc.so.6")
    buff = create_string_buffer(len(byte_procname) + 1)
    buff.value = byte_procname

    # This calls option PR_SET_NAME using it's int value of 15
    libc.prctl(15, byref(buff), 0, 0, 0)
