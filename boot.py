import os

profiles = ["A", "B", "C", "D"]
functions = ["F1","F2","F3","F4","F5","F6","F7","F8"]

required_files = [
    "PROFILE ACTIONS/onBegin.txt",
    "PROFILE ACTIONS/onEnd.txt",
    "PROFILE ACTIONS/onPress.txt",
    "PROFILE ACTIONS/onRelease.txt",

    "ROTARY ENCODER/onPress.txt",
    "ROTARY ENCODER/onRelease.txt",
    "ROTARY ENCODER/onRotateLeft.txt",
    "ROTARY ENCODER/onRotateRight.txt",
]

# cria pasta se não existir
def ensure_dir(path):
    try:
        os.mkdir(path)
        print("Criado diretório:", path)
    except OSError:
        pass

# cria arquivo vazio se não existir
def ensure_file(path):
    try:
        with open(path, "r"):
            pass
    except OSError:
        try:
            with open(path, "w") as f:
                f.write("")
            print("Criado arquivo:", path)
        except Exception as e:
            print("Erro criando arquivo:", path, e)

# estrutura principal
ensure_dir("/MACROS")

for profile in profiles:

    profile_path = f"/MACROS/{profile}"
    ensure_dir(profile_path)

    # PROFILE ACTIONS
    ensure_dir(f"{profile_path}/PROFILE ACTIONS")

    # ROTARY ENCODER
    ensure_dir(f"{profile_path}/ROTARY ENCODER")

    # F1-F8
    for function in functions:
        ensure_dir(f"{profile_path}/{function}")

    # arquivos padrão
    for file in required_files:
        ensure_file(f"{profile_path}/{file}")

    # arquivos F1-F8
    for function in functions:
        ensure_file(f"{profile_path}/{function}/onPress.txt")
        ensure_file(f"{profile_path}/{function}/onRelease.txt")


