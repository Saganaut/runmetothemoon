import ctypes
import time

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
  _fields_ = [("wVk", ctypes.c_ushort),
              ("wScan", ctypes.c_ushort),
              ("dwFlags", ctypes.c_ulong),
              ("time", ctypes.c_ulong),
              ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
  _fields_ = [("uMsg", ctypes.c_ulong),
              ("wParamL", ctypes.c_short),
              ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
  _fields_ = [("dx", ctypes.c_long),
              ("dy", ctypes.c_long),
              ("mouseData", ctypes.c_ulong),
              ("dwFlags", ctypes.c_ulong),
              ("time",ctypes.c_ulong),
              ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
  _fields_ = [("ki", KeyBdInput),
              ("mi", MouseInput),
              ("hi", HardwareInput)]

class Input(ctypes.Structure):
  _fields_ = [("type", ctypes.c_ulong),
              ("ii", Input_I)]

# Actuals Functions

def press_key(hexKeyCode):
  extra = ctypes.c_ulong(0)
  ii_ = Input_I()
  ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
  x = Input( ctypes.c_ulong(1), ii_ )
  ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(hexKeyCode):
  extra = ctypes.c_ulong(0)
  ii_ = Input_I()
  ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
  x = Input( ctypes.c_ulong(1), ii_ )
  ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def hit_key(key0, delay, key1=None):
  press_key(key0)
  if not key1 == None:
    press_key(key1)
  time.sleep(delay)
  release_key(key0)
  if not key1 == None:
    release_key(key1)

# directx scan codes http://www.gamespp.com/directx/directInputKeyboardScanCodes.html
#define DIK_Q               0x10
#define DIK_W               0x11
#define DIK_O               0x18
#define DIK_P               0x19
#define DIK_SPACE           0x39
# if __name__ == '__main__':
