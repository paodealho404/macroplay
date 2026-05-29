import time
import supervisor
import gc
import board
import digitalio
import pwmio
import rotaryio
import neopixel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.mouse import Mouse


mouse = Mouse(usb_hid.devices)
consumer_control = ConsumerControl(usb_hid.devices)
buzzer = pwmio.PWMOut(board.GP16, variable_frequency=True)

led = neopixel.NeoPixel(board.GP12, 12)
# led = neopixel.NeoPixel(board.GP12, 12, auto_write=False)


# teste de enumeração USB
while not supervisor.runtime.usb_connected:
    # Aguarda enumeração USB rápida
    time.sleep(0.5)
    for i in range(0, 50):
        if supervisor.runtime.usb_connected:
            break
        led.fill((i, i, 0))
        time.sleep(0.05)

    for i in range(50, -1, -1):
        if supervisor.runtime.usb_connected:
            break
        led.fill((i, i, 0))
        time.sleep(0.05)


contextSwitch = None
contextLED = None


encoder = rotaryio.IncrementalEncoder(board.GP13, board.GP14)

lastEncoderPosition = encoder.position

ENC_BTN = board.GP15


def playTone(freq, volume=32768):
    buzzer.frequency = freq
    buzzer.duty_cycle = volume


def stopTone():
    buzzer.duty_cycle = 0


keyBoard = Keyboard(usb_hid.devices)


# led = {
#    "A": 0,
#    "B": 1,
#    "C": 2,
#    "D": 3,
#    "F1": 7,
#    "F2": 6,
#    "F3": 5,
#    "F4": 4,
#    "F5": 8,
#    "F6": 9,
#    "F7": 10,
#    "F8": 11,
# }


LedCode = {
    "F1": 0,
    "F2": 1,
    "F3": 2,
    "F4": 3,
    "F5": 7,
    "F6": 6,
    "F7": 5,
    "F8": 4,
    "A": 8,
    "B": 9,
    "C": 10,
    "D": 11,
}


profileSwitches = ["A", "B", "C", "D"]
functionSwitches = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"]

scriptsList = {}
compiledScripts = {}

PROFILE_ACTIONS = ("onBegin", "onEnd", "onPress", "onRelease")
ENCODER_ACTIONS = ("onPress", "onRelease", "onRotateLeft", "onRotateRight")

# switchPins = {
#    "A": board.GP0,
#    "B": board.GP1,
#    "C": board.GP2,
#    "D": board.GP3,
#    "F1": board.GP4,
#    "F2": board.GP5,
#    "F3": board.GP6,
#    "F4": board.GP7,
#    "F5": board.GP8,
#    "F6": board.GP9,
#    "F7": board.GP10,
#    "F8": board.GP11,
# }


switchPins = {
    "F1": board.GP0,
    "F2": board.GP1,
    "F3": board.GP2,
    "F4": board.GP3,
    "F5": board.GP4,
    "F6": board.GP5,
    "F7": board.GP6,
    "F8": board.GP7,
    "A": board.GP8,
    "B": board.GP9,
    "C": board.GP10,
    "D": board.GP11,
}

# Configuração dos botões
switches = {}
for switch, pin in switchPins.items():
    switchPin = digitalio.DigitalInOut(pin)
    switchPin.direction = digitalio.Direction.INPUT
    switchPin.pull = digitalio.Pull.DOWN
    switches[switch] = switchPin

last_states = {switch: False for switch in switches}


encoderButton = digitalio.DigitalInOut(ENC_BTN)
encoderButton.direction = digitalio.Direction.INPUT
encoderButton.pull = digitalio.Pull.DOWN

lastEncoderButton = encoderButton.value


def importScript(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except OSError:
        return ""


def addScript(scripts, path):
    scripts[path] = importScript(path)


# Carrega todos os scripts de um perfil (A, B, C, D)
def selectProfile(profile):
    scripts = {}

    # PROFILE ACTIONS
    for action in PROFILE_ACTIONS:
        addScript(scripts, f"/MACROS/{profile}/PROFILE ACTIONS/{action}.txt")

    # ROTARY ENCODER
    for action in ENCODER_ACTIONS:
        addScript(scripts, f"/MACROS/{profile}/ROTARY ENCODER/{action}.txt")

    # FUNCTION SWITCHES
    for function in functionSwitches:
        addScript(scripts, f"/MACROS/{profile}/{function}/onPress.txt")
        addScript(scripts, f"/MACROS/{profile}/{function}/onRelease.txt")

    return scripts


def scriptError(path, e):
    print(f"Erro em: {path}: {e}")
    playTone(263, 50000)
    time.sleep(0.2)
    playTone(349, 50000)
    time.sleep(0.2)
    stopTone()


sandboxBase = {
    "led": led,
    "LedCode": LedCode.copy(),
    "keyboard": keyBoard,
    "Keycode": Keycode,
    "mouse": mouse,
    "time": time,
    "contextSwitch": contextSwitch,
    "contextLED": contextLED,
    "switches": switches.copy(),
    "consumer_control": consumer_control,
    "ConsumerControlCode": ConsumerControlCode,
    "playTone": playTone,
    "stopTone": stopTone,
}

globalVars = {
    "channel": True,
    "buttonPressed": 0,
    "ledActive": True,
    "ledState": [],
    "octave": 0,
}


def runScript(path):
    script = scriptsList.get(path, "")

    if not script:
        return False

    # Verifica RAM livre
    if gc.mem_free() < 20000:
        compiledScripts.clear()
        gc.collect()

    if path not in compiledScripts:
        try:
            compiledScripts[path] = compile(script, path, "exec")
        except Exception as e:
            # erro de sintaxe
            scriptError(path, e)
            return False

    sandbox = sandboxBase.copy()
    sandbox["contextSwitch"] = contextSwitch
    sandbox["contextLED"] = contextLED
    sandbox["LedCode"] = LedCode.copy()
    sandbox["switches"] = switches.copy()
    sandbox["globalVars"] = globalVars

    try:
        exec(compiledScripts[path], sandbox)
        return True
    except Exception as e:
        # erros de execução
        scriptError(path, e)
        return False


currentProfile = ""
led.fill((0, 0, 0))

lastGC = time.monotonic()

while True:
    if time.monotonic() - lastGC > 5:
        gc.collect()
        lastGC = time.monotonic()

    # Checar botões de seleção de perfil
    for profile in profileSwitches:
        contextSwitch = switches[profile]
        contextLED = LedCode[profile]
        current = contextSwitch.value
        if current and not last_states[profile]:
            if currentProfile != "":
                runScript(f"/MACROS/{currentProfile}/PROFILE ACTIONS/onEnd.txt")
            else:
                encoder.position = 0

            currentProfile = profile
            scriptsList = selectProfile(currentProfile)

            runScript(f"/MACROS/{currentProfile}/PROFILE ACTIONS/onBegin.txt")

            runScript(f"/MACROS/{currentProfile}/PROFILE ACTIONS/onPress.txt")

            while contextSwitch.value:
                time.sleep(0.01)

            runScript(f"/MACROS/{currentProfile}/PROFILE ACTIONS/onRelease.txt")

        last_states[profile] = current

    # Checar se o perfil foi escolhido
    if currentProfile == "":
        for function in functionSwitches:
            last_states[function] = switches[function].value
        time.sleep(0.01)
        continue

    # Checar switch de funções
    for function in functionSwitches:
        contextSwitch = switches[function]
        contextLED = LedCode[function]
        current = contextSwitch.value
        if current and not last_states[function]:
            runScript(f"/MACROS/{currentProfile}/{function}/onPress.txt")
        if not current and last_states[function]:
            runScript(f"/MACROS/{currentProfile}/{function}/onRelease.txt")
        last_states[function] = current

    # Checar botão encolder
    currentEncoderButton = encoderButton.value
    if currentEncoderButton and not lastEncoderButton:
        runScript(f"/MACROS/{currentProfile}/ROTARY ENCODER/onPress.txt")
    if not currentEncoderButton and lastEncoderButton:
        runScript(f"/MACROS/{currentProfile}/ROTARY ENCODER/onRelease.txt")
    lastEncoderButton = currentEncoderButton

    # Checar rotação do encolder
    currentPosition = encoder.position
    delta = currentPosition - lastEncoderPosition

    if delta > 0:
        for _ in range(delta):
            runScript(f"/MACROS/{currentProfile}/ROTARY ENCODER/onRotateRight.txt")

    elif delta < 0:
        for _ in range(-delta):
            runScript(f"/MACROS/{currentProfile}/ROTARY ENCODER/onRotateLeft.txt")

    lastEncoderPosition = currentPosition
    time.sleep(0.001)
