import smbus


I2C_BUS = 1
OLED_ADDRESS = 0x3C

WIDTH = 128
HEIGHT = 64

DISPLAY_OFF = 0xAE
DISPLAY_ON = 0xAF
SET_CONTRAST = 0x81
NORMAL_DISPLAY = 0xA6
SET_DISPLAY_CLOCK = 0xD5
SET_MULTIPLEX = 0xA8
SET_DISPLAY_OFFSET = 0xD3
SET_START_LINE = 0x40
CHARGE_PUMP = 0x8D
MEMORY_MODE = 0x20
COLUMN_ADDR = 0x21
PAGE_ADDR = 0x22
SEG_REMAP = 0xA1
COM_SCAN_DEC = 0xC8
SET_COM_PINS = 0xDA


FONT = {
    " ": [0x00, 0x00, 0x00, 0x00, 0x00],

    "A": [0x7E, 0x11, 0x11, 0x7E, 0x00],
    "B": [0x7F, 0x49, 0x49, 0x36, 0x00],
    "C": [0x3E, 0x41, 0x41, 0x22, 0x00],
    "D": [0x7F, 0x41, 0x41, 0x3E, 0x00],
    "E": [0x7F, 0x49, 0x49, 0x41, 0x00],
    "F": [0x7F, 0x09, 0x09, 0x01, 0x00],
    "G": [0x3E, 0x41, 0x49, 0x7A, 0x00],
    "H": [0x7F, 0x08, 0x08, 0x7F, 0x00],
    "I": [0x41, 0x7F, 0x41, 0x00, 0x00],
    "J": [0x20, 0x40, 0x41, 0x3F, 0x00],
    "K": [0x7F, 0x08, 0x14, 0x63, 0x00],
    "L": [0x7F, 0x40, 0x40, 0x40, 0x00],
    "M": [0x7F, 0x06, 0x06, 0x7F, 0x00],
    "N": [0x7F, 0x06, 0x18, 0x7F, 0x00],
    "O": [0x3E, 0x41, 0x41, 0x3E, 0x00],
    "P": [0x7F, 0x09, 0x09, 0x06, 0x00],
    "Q": [0x3E, 0x41, 0x61, 0x7E, 0x00],
    "R": [0x7F, 0x09, 0x19, 0x66, 0x00],
    "S": [0x46, 0x49, 0x49, 0x31, 0x00],
    "T": [0x01, 0x7F, 0x01, 0x00, 0x00],
    "U": [0x3F, 0x40, 0x40, 0x3F, 0x00],
    "V": [0x1F, 0x20, 0x40, 0x20, 0x1F],
    "W": [0x7F, 0x30, 0x30, 0x7F, 0x00],
    "X": [0x63, 0x14, 0x08, 0x14, 0x63],
    "Y": [0x03, 0x04, 0x78, 0x04, 0x03],
    "Z": [0x61, 0x51, 0x49, 0x45, 0x43],

    ":": [0x00, 0x36, 0x36, 0x00, 0x00],
    ".": [0x00, 0x60, 0x60, 0x00, 0x00],
    "-": [0x08, 0x08, 0x08, 0x08, 0x00],

    "0": [0x3E, 0x45, 0x49, 0x51, 0x3E],
    "1": [0x00, 0x21, 0x7F, 0x01, 0x00],
    "2": [0x21, 0x43, 0x45, 0x39, 0x00],
    "3": [0x42, 0x41, 0x51, 0x6E, 0x00],
    "4": [0x0C, 0x14, 0x24, 0x7F, 0x00],
    "5": [0x72, 0x51, 0x51, 0x4E, 0x00],
    "6": [0x1E, 0x29, 0x49, 0x06, 0x00],
    "7": [0x40, 0x47, 0x48, 0x70, 0x00],
    "8": [0x36, 0x49, 0x49, 0x36, 0x00],
    "9": [0x30, 0x49, 0x4A, 0x3C, 0x00],
}


class SSD1306:
    def __init__(self):
        self.bus = smbus.SMBus(I2C_BUS)
        self.buffer = bytearray(WIDTH * HEIGHT // 8)
        self._initialize()

    def command(self, value):
        self.bus.write_byte_data(OLED_ADDRESS, 0x00, value)

    def _initialize(self):
        commands = [
            DISPLAY_OFF,
            SET_DISPLAY_CLOCK,
            0x80,
            SET_MULTIPLEX,
            0x3F,
            SET_DISPLAY_OFFSET,
            0x00,
            SET_START_LINE,
            CHARGE_PUMP,
            0x14,
            MEMORY_MODE,
            0x00,
            SEG_REMAP,
            COM_SCAN_DEC,
            SET_COM_PINS,
            0x12,
            SET_CONTRAST,
            0x7F,
            NORMAL_DISPLAY,
            DISPLAY_ON,
        ]

        for command in commands:
            self.command(command)

        self.clear()
        self.show()

    def clear(self):
        self.buffer[:] = b"\x00" * len(self.buffer)

    def pixel(self, x, y, value=1):
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            return

        index = x + (y // 8) * WIDTH
        bit = y % 8

        if value:
            self.buffer[index] |= 1 << bit
        else:
            self.buffer[index] &= ~(1 << bit)

    def draw_char(self, x, y, char):
        bitmap = FONT.get(char.upper(), FONT[" "])

        for column, data in enumerate(bitmap):
            for row in range(7):
                if data & (1 << row):
                    self.pixel(x + column, y + row)

    def draw_text(self, x, y, text):
        cursor_x = x

        for char in text:
            self.draw_char(cursor_x, y, char)
            cursor_x += 6

    def show_status(
        self,
        plex,
        abs_status,
        windows_agent,
        cpu=None,
        memory=None,
        disk=None,
    ):
        self.clear()

        def status_text(value):
            if value is None:
                return "CHECKING"

            return "ONLINE" if value else "OFFLINE"

        self.draw_text(
            0,
            0,
            f"Plex: {status_text(plex)}"
        )

        self.draw_text(
            0,
            12,
            f"ABS: {status_text(abs_status)}"
        )

        self.draw_text(
            0,
            24,
            f"Agent: {status_text(windows_agent)}"
        )

        if cpu is not None and memory is not None:
            self.draw_text(
                0,
                40,
                f"CPU:{cpu:.0f}%  RAM:{memory:.0f}%"
            )

        if disk is not None:
            self.draw_text(
                0,
                52,
                f"Disk:{disk:.0f}%"
            )

        self.show()

    def show(self):
        self.command(COLUMN_ADDR)
        self.command(0)
        self.command(WIDTH - 1)

        self.command(PAGE_ADDR)
        self.command(0)
        self.command((HEIGHT // 8) - 1)

        for start in range(0, len(self.buffer), 32):
            chunk = self.buffer[start:start + 32]

            self.bus.write_i2c_block_data(
                OLED_ADDRESS,
                0x40,
                list(chunk),
            )

    def close(self):
        self.bus.close()