import sys
import termios
import tty
import click
import yaml
from gpiozero import Servo, Device
from gpiozero.pins.rpigpio import RPiGPIOFactory
import os

# Set the pin factory to RPiGPIOFactory for software PWM
Device.pin_factory = RPiGPIOFactory()

# Define the servos with GPIO pins
SERVOS = {
    "claw": Servo(17, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # purple wire - claw
    "wrist": Servo(18, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # blue wire - wrist
    "lower_arm": Servo(22, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # green wire - lower_arm
    "upper_arm": Servo(23, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # yellow wire - upper_arm
    "shoulder": Servo(24, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # orange wire - shoulder
    "base": Servo(25, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # red wire - base
}

# YAML state files
STATE_FILE = "servo_states.yaml"
RECENT_STATE_FILE = "recent_servo_states.yaml"

# Initialize SERVO_POSITIONS (0-100 scale or 'off') for each servo
DEFAULT_SERVO_POSITIONS = {name: "off" for name in SERVOS}  # Default to off

# Helper function to save SERVO_POSITIONS to a YAML file
def save_state_to_yaml(state, file_path):
    with open(file_path, "w") as f:
        yaml.dump(state, f)

# Helper function to load SERVO_POSITIONS from a YAML file
def load_state_from_yaml(file_path, default_state):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return yaml.safe_load(f) or default_state
    else:
        return default_state

# Load recent positions or initialize with defaults
SERVO_POSITIONS = load_state_from_yaml(RECENT_STATE_FILE, DEFAULT_SERVO_POSITIONS)

# Set all servos to the loaded SERVO_POSITIONS or turn them off
for name, servo in SERVOS.items():
    if SERVO_POSITIONS[name] == "off":
        servo.value = None  # Turn off servo
    else:
        normalized_value = (SERVO_POSITIONS[name] - 50) / 50  # Convert 0-100 scale to -1 to 1
        servo.value = normalized_value

# Function to read a single character from stdin
def get_single_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Interactive CLI
@click.command()
def cli():
    "Interactive CLI tool to control servos"
    while True:
        print("\n" + "-" * 80)
        print("Select servo:")
        for idx, name in enumerate(SERVOS.keys(), start=1):
            print(f"{idx}. {name}")
        print("-" * 40)
        print("Other options:")
        print(f"{len(SERVOS) + 1}. Save all servo positions")
        print(f"{len(SERVOS) + 2}. Exit")
        print()

        print("Select an option: ", end="", flush=True)
        choice = get_single_char()
        print(choice)  # Echo the choice

        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(SERVOS):
                servo_name = list(SERVOS.keys())[choice - 1]
                control_servo(servo_name)
            elif choice == len(SERVOS) + 1:
                save_all()
            elif choice == len(SERVOS) + 2:
                print("Exiting CLI tool.")
                save_state_to_yaml(SERVO_POSITIONS, RECENT_STATE_FILE)
                break
            else:
                print("Invalid selection. Please try again.")
        elif choice.lower() == 'q':
            print("Exiting CLI tool.")
            save_state_to_yaml(SERVO_POSITIONS, RECENT_STATE_FILE)
            break
        else:
            print("Invalid input. Please enter a valid option.")

# Function to control a specific servo
def control_servo(servo_name):
    servo = SERVOS[servo_name]
    print(f"\nControlling {servo_name}. Enter values between 0-100, 'off' to turn off, 'save' to save state, or 'q' to return to the main menu.")
    while True:
        cmd = input(f"{servo_name} > ")
        if cmd.lower() in ["exit", "q"]:
            print(f"Exiting control mode for {servo_name}.")
            break
        elif cmd.lower() == "save":
            print(f"Saving {servo_name} position ({SERVO_POSITIONS[servo_name]}) to YAML.")
            save_state_to_yaml({servo_name: SERVO_POSITIONS[servo_name]}, STATE_FILE)
        elif cmd.lower() == "off":
            print(f"Turning off {servo_name}.")
            SERVO_POSITIONS[servo_name] = "off"
            servo.value = None  # Turn off servo
        elif cmd.isdigit() and 0 <= int(cmd) <= 100:
            value = int(cmd)
            SERVO_POSITIONS[servo_name] = value
            normalized_value = (value - 50) / 50  # Convert 0-100 scale to -1 to 1
            servo.value = normalized_value
        else:
            print("Invalid command. Type a number between 0-100, 'off', 'save', or 'q'.")

# Function to save all SERVO_POSITIONS
def save_all():
    print("Saving all servo SERVO_POSITIONS to YAML.")
    save_state_to_yaml(SERVO_POSITIONS, STATE_FILE)
    print("All SERVO_POSITIONS saved.")

if __name__ == "__main__":
    cli()
