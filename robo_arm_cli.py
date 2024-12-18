import click
import yaml
from gpiozero import Servo
from time import sleep
import os

# Define the servos with GPIO pins
SERVOS = {
    "claw": Servo(17, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # purple wire - claw
    "wrist": Servo(18, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # blue wire - wrist
    "lower_arm": Servo(22, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # green wire - lower_arm
    "upper_arm": Servo(23, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # yellow wire - upper_arm
    "shoulder": Servo(24, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # orange wire - shoulder
    "base": Servo(25, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000),  # red wire - base
}

# Initialize positions (0-100 scale) for each servo
positions = {name: 50 for name in SERVOS}  # Default to mid-position

# YAML state files
STATE_FILE = "servo_states.yaml"
RECENT_STATE_FILE = "recent_servo_states.yaml"

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

# Set all servos to the loaded positions and hold them
for name, servo in SERVOS.items():
    normalized_value = (positions[name] - 50) / 50  # Convert 0-100 scale to -1 to 1
    servo.value = normalized_value
    sleep(0.5)
    servo.hold()

# CLI group
@click.group()
def cli():
    "CLI tool to control servos"
    pass

# Command to control individual servos
@cli.command()
@click.argument("servo_name", type=click.Choice(SERVOS.keys()))
def control(servo_name):
    "Control a specific servo"
    servo = SERVOS[servo_name]
    print(f"Selected {servo_name}. Type values between 0-100 to move it, 'save' to save position, or 'save_all' to save all positions.")
    try:
        while True:
            cmd = input(f"{servo_name} > ")
            if cmd.lower() == "save":
                print(f"Saving {servo_name} position ({positions[servo_name]}) to YAML.")
                save_state_to_yaml({servo_name: positions[servo_name]}, STATE_FILE)
            elif cmd.lower() == "save_all":
                print("Saving all servo positions to YAML.")
                save_state_to_yaml(positions, STATE_FILE)
                print("All positions saved.")
            elif cmd.isdigit() and 0 <= int(cmd) <= 100:
                value = int(cmd)
                positions[servo_name] = value
                normalized_value = (value - 50) / 50  # Convert 0-100 scale to -1 to 1
                servo.value = normalized_value
                sleep(0.5)  # Allow the servo to reach position
                servo.hold()  # Hold position
            else:
                print("Invalid command. Type a number between 0-100, 'save', or 'save_all'.")
    except KeyboardInterrupt:
        print(f"Exiting control mode for {servo_name}.")
        servo.hold()

# Command to save all positions
@cli.command()
def save_all():
    "Save all servo positions to YAML"
    print("Saving all servo positions to YAML.")
    save_state_to_yaml(positions, STATE_FILE)
    print("All positions saved.")

# Main entry point
if __name__ == "__main__":
    try:
        save_state_to_yaml(positions, RECENT_STATE_FILE)  # Save recent positions at startup
        cli()
    except KeyboardInterrupt:
        print("Exiting CLI tool. Resetting all servos to hold position.")
        for servo in SERVOS.values():
            servo.hold()
