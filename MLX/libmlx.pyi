import ctypes


lib: str
lib_name: str
mlx: ctypes.CDLL

# ============================================================================
# Type Aliases (re-exported ctypes scalar types used throughout the module)
# ============================================================================

c_int32 = ctypes.c_int32
c_uint32 = ctypes.c_uint32
c_uint8 = ctypes.c_uint8
c_size_t = ctypes.c_size_t
c_bool = ctypes.c_bool
c_double = ctypes.c_double
c_char_p = ctypes.c_char_p
c_void_p = ctypes.c_void_p

# keys_t

MLX_KEY_SPACE: int
MLX_KEY_APOSTROPHE: int
MLX_KEY_COMMA: int
MLX_KEY_MINUS: int
MLX_KEY_PERIOD: int
MLX_KEY_SLASH: int
MLX_KEY_0: int
MLX_KEY_1: int
MLX_KEY_2: int
MLX_KEY_3: int
MLX_KEY_4: int
MLX_KEY_5: int
MLX_KEY_6: int
MLX_KEY_7: int
MLX_KEY_8: int
MLX_KEY_9: int
MLX_KEY_SEMICOLON: int
MLX_KEY_EQUAL: int
MLX_KEY_A: int
MLX_KEY_B: int
MLX_KEY_MENU: int


# cursor_t
MLX_CURSOR_ARROW: int
MLX_CURSOR_IBEAM: int
MLX_CURSOR_CROSSHAIR: int
MLX_CURSOR_HAND: int
MLX_CURSOR_HRESIZE: int
MLX_CURSOR_VRESIZE: int

# mouse_mode_t
MLX_MOUSE_NORMAL: int
MLX_MOUSE_HIDDEN: int
MLX_MOUSE_DISABLED: int

# mouse_key_t
MLX_MOUSE_BUTTON_LEFT: int
MLX_MOUSE_BUTTON_RIGHT: int
MLX_MOUSE_BUTTON_MIDDLE: int

# modifier_key_t
MLX_SHIFT: int
MLX_CONTROL: int
MLX_ALT: int
MLX_SUPERKEY: int
MLX_CAPSLOCK: int
MLX_NUMLOCK: int

# action state
MLX_RELEASE: int
MLX_PRESS: int
MLX_REPEAT: int

# mlx_settings_t
MLX_STRETCH_IMAGE: int
MLX_FULLSCREEN: int
MLX_MAXIMIZED: int
MLX_DECORATED: int
MLX_HEADLESS: int
MLX_SETTINGS_MAX: int

# Structures
# ============================================================================

class mlx_texture_t(ctypes.Structure):
    width: int
    height: int
    bytes_per_pixel: int
    pixels: ctypes._Pointer[ctypes.c_uint8]

class mlx_instance_t(ctypes.Structure):
    x: int
    y: int
    z: int
    enabled: bool

class xpm_t(ctypes.Structure):
    texture: mlx_texture_t
    color_count: int
    cpp: int
    mode: bytes

class mlx_key_data_t(ctypes.Structure):
    key: int
    action: int
    os_key: int
    modifier: int

class mlx_image_t(ctypes.Structure):
    width: int
    height: int
    pixels: ctypes._Pointer[ctypes.c_uint8]
    instances: ctypes._Pointer[mlx_instance_t]
    count: int
    enabled: bool
    context: int | None

class mlx_t(ctypes.Structure):
    window: int | None
    context: int | None
    width: int
    height: int
    delta_time: float

# Function Callback Types
# ============================================================================

mlx_scrollfunc = ctypes.CFUNCTYPE(None, c_double, c_double, c_void_p)
mlx_mousefunc = ctypes.CFUNCTYPE(None, c_int32, c_int32, c_int32, c_void_p)
mlx_cursorfunc = ctypes.CFUNCTYPE(None, c_double, c_double, c_void_p)
mlx_keyfunc = ctypes.CFUNCTYPE(None, mlx_key_data_t, c_void_p)
mlx_resizefunc = ctypes.CFUNCTYPE(None, c_int32, c_int32, c_void_p)
mlx_closefunc = ctypes.CFUNCTYPE(None, c_void_p)
mlx_loop_hook_func = ctypes.CFUNCTYPE(None, c_void_p)

# Function Signatures
# ============================================================================

# Error
def mlx_strerror(errno: int) -> bytes | None: ...
def mlx_get_errno() -> int: ...

# Generic MLX Functions
def mlx_init(
    width: int,
    height: int,
    title: bytes,
    resize: bool,
) -> ctypes._Pointer[mlx_t]: ...

def mlx_set_setting(setting: int, value: int) -> None: ...
def mlx_close_window(mlx: ctypes._Pointer[mlx_t]) -> None: ...
def mlx_loop(mlx: ctypes._Pointer[mlx_t]) -> None: ...
def mlx_terminate(mlx: ctypes._Pointer[mlx_t]) -> None: ...
def mlx_get_time() -> float: ...


# Image Functions
def mlx_put_pixel(
    image: ctypes._Pointer[mlx_image_t],
    x: int,
    y: int,
    color: int,
) -> None: ...

def mlx_new_image(
    mlx: ctypes._Pointer[mlx_t],
    width: int,
    height: int,
) -> ctypes._Pointer[mlx_image_t]: ...

def mlx_image_to_window(
    mlx: ctypes._Pointer[mlx_t],
    image: ctypes._Pointer[mlx_image_t],
    x: int,
    y: int,
) -> int: ...

def mlx_delete_image(
    mlx: ctypes._Pointer[mlx_t],
    image: ctypes._Pointer[mlx_image_t],
) -> None: ...

# Input
def mlx_is_key_down(mlx: ctypes._Pointer[mlx_t], key: int) -> bool: ...

# Hooks
def mlx_loop_hook(
    mlx: ctypes._Pointer[mlx_t],
    callback: ctypes._FuncPointer,
    param: int | None,
) -> bool: ...
