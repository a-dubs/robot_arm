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

# Initialize positions (0-100 scale) for each servo
positions = {name: 50 for name in SERVOS}  # Default to mid-position

# Helper function to save positions to a YAML file
def save_state_to_yaml(state, file_path):
    with open(file_path, "w") as f:
        yaml.dump(state, f)

# Helper function to load positions from a YAML file
def load_state_from_yaml(file_path, default_state):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return yaml.safe_load(f) or default_state
    else:
        return default_state

# Load recent positions or initialize with defaults
positions = load_state_from_yaml(RECENT_STATE_FILE, positions)

# Set all servos to the loaded positions
for name, servo in SERVOS.items():
    normalized_value = (positions[name] - 50) / 50  # Convert 0-100 scale to -1 to 1
    servo.value = normalized_value

# Interactive CLI
@click.command()
def cli():
    "Interactive CLI tool to control servos"
    while True:
        print("\nMain Menu:")
        print("1. Select a servo to control")
        print("2. Save all servo positions")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            print("\nAvailable Servos:")
            for idx, name in enumerate(SERVOS.keys(), start=1):
                print(f"{idx}. {name}")
            servo_choice = input("Select a servo by name or number: ")

            servo_name = None
            if servo_choice.isdigit():
                index = int(servo_choice) - 1
                if 0 <= index < len(SERVOS):
                    servo_name = list(SERVOS.keys())[index]
            elif servo_choice in SERVOS:
                servo_name = servo_choice

            if servo_name:
                control_servo(servo_name)
            else:
                print("Invalid selection.")

        elif choice == "2":
            save_all()
        elif choice == "3":
            print("Exiting CLI tool.")
            save_state_to_yaml(positions, RECENT_STATE_FILE)
            break
        else:
            print("Invalid choice. Please try again.")

# Function to control a specific servo
def control_servo(servo_name):
    servo = SERVOS[servo_name]
    print(f"\nControlling {servo_name}. Enter values between 0-100, 'save' to save state, or 'exit' to return to the main menu.")
    while True:
        cmd = input(f"{servo_name} > ")
        if cmd.lower() == "exit":
            print(f"Exiting control mode for {servo_name}.")
            break
        elif cmd.lower() == "save":
            print(f"Saving {servo_name} position ({positions[servo_name]}) to YAML.")
            save_state_to_yaml({servo_name: positions[servo_name]}, STATE_FILE)
        elif cmd.isdigit() and 0 <= int(cmd) <= 100:
            value = int(cmd)
            positions[servo_name] = value
            normalized_value = (value - 50) / 50  # Convert 0-100 scale to -1 to 1
            servo.value = normalized_value
        else:
            print("Invalid command. Type a number between 0-100, 'save', or 'exit'.")

# Function to save all positions
def save_all():
    print("Saving all servo positions to YAML.")
    save_state_to_yaml(positions, STATE_FILE)
    print("All positions saved.")

if __name__ == "__main__":
    cli()
