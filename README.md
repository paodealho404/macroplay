# MACROPLAY

MACROPLAY é um firmware em CircuitPython e editor web para um macro pad USB HID baseado em RP2040. O projeto permite configurar 4 perfis independentes, 8 teclas de função, encoder rotativo, LEDs NeoPixel e buzzer, executando macros escritas em Python/CircuitPython a partir de arquivos `.txt` armazenados no próprio drive `CIRCUITPY`.

## Visão Geral

O firmware roda diretamente na placa e monitora botões, perfis e encoder. Cada ação do dispositivo dispara um script específico salvo na pasta MACROS, permitindo criar atalhos de teclado, comandos de mouse, controles de mídia, efeitos de LED e feedback sonoro.

O repositório também inclui o **MACROPLAY Editor**, uma interface HTML local para abrir a pasta da placa, editar macros com destaque de sintaxe e salvar os arquivos diretamente no dispositivo.

## Principais Recursos

- 4 perfis configuráveis: `A`, `B`, `C` e `D`
- 8 teclas de função por perfil: `F1` até `F8`
- Eventos separados para pressionar e soltar cada tecla
- Encoder rotativo com eventos de giro para esquerda, giro para direita, press e release
- Ações de ciclo de vida do perfil: ativar, desativar, pressionar e soltar
- Suporte a teclado, mouse e controles de mídia via USB HID
- Controle de LEDs NeoPixel para feedback visual
- Controle de buzzer para feedback sonoro
- Scripts carregados dinamicamente a partir da pasta MACROS
- Cache de scripts compilados com limpeza automática de memória
- Editor web local com CodeMirror, autocomplete, salvar/recarregar arquivos e suporte à File System Access API

## Estrutura de Macros

As macros ficam organizadas por perfil e evento:

```text
MACROS/
  A/
    F1/
      onPress.txt
      onRelease.txt
    F2/
      onPress.txt
      onRelease.txt
    ...
    PROFILE ACTIONS/
      onBegin.txt
      onEnd.txt
      onPress.txt
      onRelease.txt
    ROTARY ENCODER/
      onPress.txt
      onRelease.txt
      onRotateLeft.txt
      onRotateRight.txt
  B/
  C/
  D/
```

## Eventos Disponíveis

### Teclas F1-F8

- onPress.txt: executado quando a tecla é pressionada
- onRelease.txt: executado quando a tecla é solta

### Perfil

- onBegin.txt: executado ao ativar o perfil
- onEnd.txt: executado ao sair do perfil atual
- onPress.txt: executado ao pressionar o botão do perfil
- onRelease.txt: executado ao soltar o botão do perfil

### Encoder Rotativo

- onPress.txt: executado ao pressionar o botão do encoder
- onRelease.txt: executado ao soltar o botão do encoder
- onRotateLeft.txt: executado ao girar para a esquerda
- onRotateRight.txt: executado ao girar para a direita

## APIs Disponíveis nas Macros

Os scripts das macros podem usar objetos e funções expostos pelo firmware:

```python
keyboard.send(Keycode.CONTROL, Keycode.C)
keyboard.press(Keycode.SHIFT)
keyboard.release(Keycode.SHIFT)
keyboard.release_all()

mouse.move(x=0, y=0, wheel=1)

consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)
consumer_control.send(ConsumerControlCode.MUTE)

led[contextLED] = (0, 255, 0)
led.fill((10, 10, 10))

playTone(440)
stopTone()

time.sleep(0.2)
```

Também estão disponíveis:

- `Keycode`
- `ConsumerControlCode`
- `contextSwitch`
- `contextLED`
- `LedCode`
- `switches`
- `globalVars`

## Editor Web

O arquivo MacroPlayEditor.html fornece uma interface visual para editar as macros diretamente no navegador.

Funcionalidades principais:

- Seleção da pasta raiz do drive `CIRCUITPY`
- Leitura automática da pasta MACROS
- Abas para os perfis `A`, `B`, `C` e `D`
- Editor de código com destaque de sintaxe Python
- Autocomplete para comandos comuns do MACROPLAY
- Botões para salvar, recarregar, copiar, colar, apagar e bloquear scripts
- Indicador de alterações não salvas
- Salvamento direto nos arquivos `.txt` da placa

O editor utiliza a File System Access API, portanto deve ser aberto em um navegador baseado em Chromium, como Chrome, Edge, Brave, Opera ou Vivaldi.

## Hardware Mapeado

O firmware está configurado para o seguinte mapeamento de pinos:

| Função | Pino |
| --- | --- |
| F1 | GP0 |
| F2 | GP1 |
| F3 | GP2 |
| F4 | GP3 |
| F5 | GP4 |
| F6 | GP5 |
| F7 | GP6 |
| F8 | GP7 |
| Perfil A | GP8 |
| Perfil B | GP9 |
| Perfil C | GP10 |
| Perfil D | GP11 |
| NeoPixel | GP12 |
| Encoder A | GP13 |
| Encoder B | GP14 |
| Botão do encoder | GP15 |
| Buzzer | GP16 |

## Requisitos

- Placa RP2040 compatível com CircuitPython
- CircuitPython instalado no dispositivo
- Biblioteca `neopixel`
- Bibliotecas `adafruit_hid`
- Navegador baseado em Chromium para usar o editor web

## Como Usar

1. Copie code.py, boot.py, MacroPlayEditor.html, settings.toml, lib e MACROS para o drive `CIRCUITPY`.
2. Reinicie a placa.
3. Abra MacroPlayEditor.html no navegador.
4. Selecione a pasta raiz do drive `CIRCUITPY`.
5. Edite os scripts dos perfis, teclas e encoder.
6. Salve as alterações.
7. Use os botões físicos do macro pad para executar as macros.

## Exemplo de Macro

```python
led[contextLED] = (0, 255, 0)
keyboard.send(Keycode.CONTROL, Keycode.C)
```

```python
consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)
```

```python
playTone(440)
time.sleep(0.1)
stopTone()
```

## Sobre

MACROPLAY foi criado para transformar uma placa RP2040 em um macro pad flexível, editável e independente, combinando automação USB HID, feedback visual, feedback sonoro e um editor local simples para personalização rápida das macros.