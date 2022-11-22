import win32clipboard
from ctypes import *


class DROPFILES(Structure):
	_fields_ = [
		("pFiles", c_uint),
		("x", c_long),
		("y", c_long),
		("fNC", c_int),
		("fWide", c_bool),
	]


def setClipboardFiles(paths):
	files = ("\0".join(paths)).replace("/", "\\")
	data = files.encode("U16")[2:] + b"\0\0"
	win32clipboard.OpenClipboard()
	try:
		win32clipboard.EmptyClipboard()
		win32clipboard.SetClipboardData(
			win32clipboard.CF_HDROP, matedata + data)
	finally:
		win32clipboard.CloseClipboard()


def readClipboardFilePaths():
	win32clipboard.OpenClipboard()
	try:
		return win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
	finally:
		win32clipboard.CloseClipboard()


pDropFiles = DROPFILES()
pDropFiles.pFiles = sizeof(DROPFILES)
pDropFiles.fWide = True
matedata = bytes(pDropFiles)

