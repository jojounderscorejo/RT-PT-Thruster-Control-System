import gi
import serial
import serial.tools.list_ports

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

class SystemParameters:
    def __init__(self):
        self.num_shots              = 1
        self.firing_interval        = 1000
        self.crowbar_delay          = 35
        self.camera_delay           = 30
        # ready to fire status
        # 0 -> System idling
        # 1 -> Ready to fire
        # 2 -> Firing
        self.status                 = 0

class Messages:
    def error_sys_firing():
        message = "ERROR:\nEXCECUTION IN PROGRESS.\n\nWait until the end of excecution to change parameters"
        return message
    
    def error_sys_not_ready():
        message = "ERROR:\nNOT ARMED\n\nPlease click 'ARM SYSTEM' to arm the system."
        return message
    
    def error_none():
        message = "ERROR:\nNONE"
        return message
    
    def status_sys_idling():
        message = "Current Status:\nSYSTEM IDLING"
        return message
        
    def status_sys_firing():
        message = "Current Status:\nFIRING"
        return message
    
    def status_sys_ready():
        message = "Current Status:\nARMED"
        return message

    def error_no_arduino():
        message = "NO ARDUINO FOUND\nPlease double check connection."
        return message
    
    def error_multiple_arduino():
        message = "MULTIPLE ARUIDNOS\nPlease ensure there is only one arduino\nconnected to the computer."
        return message

class Handler:
    def on_FireControlGUI_destroy(self, *args):
        ser.close()
        Gtk.main_quit()
        
    def on_arm_system_button_clicked(self, button, *args):
        if sys_params.status != 2:
            # Changing system parameters
            sys_params.num_shots       = int(num_shots_entry.get_text())
            sys_params.firing_interval = int(firing_interval_entry.get_text())
            sys_params.crowbar_delay   = int(crowbar_delay_entry.get_text())
            # Changing system status
            sys_params.status = 1
            # Display data
            num_of_shots_display.set_label(str(sys_params.num_shots))
            firing_interval_display.set_label(str(sys_params.firing_interval))
            crowbar_delay_display.set_label(str(sys_params.crowbar_delay))
            camera_delay_display.set_label(str(sys_params.camera_delay))
            message_display.set_label(Messages.error_none())
            status_display.set_label(Messages.status_sys_ready())
        elif sys_params.status == 2:
            message_display.set_label(Messages.error_sys_firing())

    def on_excecute_button_clicked(self, button, *args):
        if sys_params.status == 1:
            self.send_arduino_data(
                sys_params.num_shots,
                sys_params.firing_interval,
                sys_params.crowbar_delay,
                sys_params.camera_delay
            )
            min_time    = sys_params.num_shots * sys_params.firing_interval
            status_display.set_label(Messages.status_sys_firing())
            GLib.timeout_add(min_time, self.status_to_idling)
        else:
            message_display.set_label(Messages.error_sys_not_ready())
    
    def status_to_idling(self):
        # This is just a work around to get GLib.timeout_add() working
        sys_params.status = 0
        status_display.set_label(Messages.status_sys_idling())
        return None
    
    def send_arduino_data(self, num_shots, firing_interval, crowbar_delay, camera_delay):
        string_to_arduino = f"{num_shots},{firing_interval},{crowbar_delay},{camera_delay}"
        ser.write(bytes(string_to_arduino, 'utf-8'))

# Initialise builder
builder = Gtk.Builder()
builder.add_from_file("FireControlGui.glade")
# builder.connect_signals(Handler())

# Get objects
window                  = builder.get_object("FireControlGUI")
# Entries
num_shots_entry         = builder.get_object("num_shots_entry")
firing_interval_entry   = builder.get_object("firing_interval_entry")
crowbar_delay_entry     = builder.get_object("crowbar_delay_entry")
camera_delay_entry      = builder.get_object("camera_delay_entry")
# Displays (Labels)
num_of_shots_display    = builder.get_object("num_of_shots_display")
firing_interval_display = builder.get_object("firing_interval_display")
crowbar_delay_display   = builder.get_object("crowbar_delay_display")
camera_delay_display    = builder.get_object("camera_delay_display")
status_display          = builder.get_object("status_display")
message_display         = builder.get_object("message_display")

# Initialise system parameters
sys_params = SystemParameters()

# Initialise Windows
num_shots_entry.set_text(str(sys_params.num_shots))
firing_interval_entry.set_text(str(sys_params.firing_interval))
crowbar_delay_entry.set_text(str(sys_params.crowbar_delay))
camera_delay_entry.set_text(str(sys_params.camera_delay))

# Initialise Serial Port communication
arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'Arduino' in p.description  # may need tweaking to match new arduinos
]
if not arduino_ports:
    message_display.set_label(Messages.error_no_arduino())
if len(arduino_ports) > 1:
    message_display.set_label(Messages.error_multiple_arduino())
if len(arduino_ports) == 1:
    ser = serial.Serial(arduino_ports[0])
    builder.connect_signals(Handler())

window.show_all()
Gtk.main()