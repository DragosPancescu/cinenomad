from ctypes import cdll, byref, create_string_buffer


def set_proc_name(procname):
    byte_procname = procname.encode("utf-8")

    libc = cdll.LoadLibrary("libc.so.6")
    buff = create_string_buffer(len(byte_procname) + 1)
    buff.value = byte_procname

    libc.prctl(15, byref(buff), 0, 0, 0)
