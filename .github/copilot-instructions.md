# Project Guidelines

## Contexto do Projeto

MACROPLAY e um firmware em CircuitPython com um editor web local para um macro pad USB HID baseado em RP2040. O dispositivo possui 4 perfis (`A` a `D`), 8 teclas de funcao (`F1` a `F8`), encoder rotativo, LEDs NeoPixel e buzzer. As macros sao scripts Python/CircuitPython salvos como arquivos `.txt` dentro de `/MACROS` no drive `CIRCUITPY`.

O objetivo do projeto e manter o teclado de macros editavel diretamente pela placa, sem depender de servidor, build step ou app instalado.

## Arquivos Principais

- `code.py`: runtime principal do firmware. Le botoes, perfis e encoder, carrega scripts de `/MACROS`, compila scripts sob demanda e executa cada evento no sandbox do firmware.
- `boot.py`: garante a estrutura minima de pastas e arquivos de macro no boot. Nao remova placeholders criados por este arquivo.
- `MacroPlayEditor.html`: editor web local. Abre a raiz do drive `CIRCUITPY`, le/escreve arquivos em `MACROS` e oferece interface para editar scripts.
- `MACROS/`: dados editaveis pelo usuario. Arquivos vazios aqui geralmente sao placeholders intencionais.
- `lib/`: bibliotecas CircuitPython usadas pelo firmware, incluindo `adafruit_hid` e `neopixel`.

## Contrato da Estrutura de Macros

Preserve esta estrutura como contrato entre firmware, boot e editor:

```text
MACROS/
  A/
    F1/
      onPress.txt
      onRelease.txt
    ...
    F8/
      onPress.txt
      onRelease.txt
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

Regras importantes:

- Nunca trate `onPress.txt` e `onRelease.txt` vazios como lixo. Eles sao placeholders necessarios para cada tecla `F1` a `F8` em todos os perfis.
- Nunca remova pastas vazias de perfis, teclas, `PROFILE ACTIONS` ou `ROTARY ENCODER` se elas fazem parte da estrutura esperada.
- Preserve exatamente os nomes `PROFILE ACTIONS` e `ROTARY ENCODER`, incluindo espacos e caixa.
- O firmware usa caminhos absolutos CircuitPython como `/MACROS/A/F1/onPress.txt`; nao troque para caminhos de desktop.
- Arquivos de evento novos so devem ser adicionados se `code.py`, `boot.py` e `MacroPlayEditor.html` forem atualizados juntos.

## Eventos Suportados

Para teclas `F1` a `F8`:

- `onPress.txt`
- `onRelease.txt`

Para acoes de perfil:

- `onBegin.txt`
- `onEnd.txt`
- `onPress.txt`
- `onRelease.txt`

Para encoder rotativo:

- `onPress.txt`
- `onRelease.txt`
- `onRotateLeft.txt`
- `onRotateRight.txt`

Nao assuma que outros nomes de evento sao usados pelo firmware. Antes de manter, documentar ou expor um evento novo, confirme que ele e carregado e executado em `code.py`.

## API Disponivel nas Macros

Os scripts de macro executados pelo firmware podem usar os objetos expostos no sandbox de `code.py`:

- `keyboard`
- `Keycode`
- `mouse`
- `consumer_control`
- `ConsumerControlCode`
- `led`
- `LedCode`
- `contextSwitch`
- `contextLED`
- `switches`
- `globalVars`
- `time`
- `playTone(freq, volume=32768)`
- `stopTone()`

Ao adicionar ou renomear APIs de macro, atualize tambem o autocomplete/destaque em `MacroPlayEditor.html` para manter a experiencia coerente.

## Regras para Firmware CircuitPython

- Escreva codigo compativel com CircuitPython no RP2040, nao com CPython completo.
- Evite dependencias novas. Se forem indispensaveis, elas precisam caber em `lib/` e rodar na placa.
- Cuide de memoria. O firmware ja usa cache de scripts compilados e `gc.collect()`; alteracoes devem respeitar RAM limitada.
- Evite loops bloqueantes longos dentro do loop principal. O teclado precisa continuar responsivo.
- Ao segurar teclas com `keyboard.press(...)`, garanta caminho claro para `keyboard.release(...)` ou `keyboard.release_all()`.
- Mantenha o boot simples e idempotente: ele pode criar pastas/arquivos faltantes, mas nao deve apagar macros do usuario.

## Hardware e Pinos

Mapeamento atual:

| Funcao | Pino |
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
| Botao do encoder | GP15 |
| Buzzer | GP16 |

Qualquer mudanca de pinagem deve ser feita em `code.py` e documentada claramente.

## Regras para o Editor Web

- `MacroPlayEditor.html` deve continuar sendo um arquivo HTML unico e abrivel localmente.
- Nao introduza build step, bundler ou servidor obrigatorio sem pedido explicito.
- O editor usa File System Access API; foque em navegadores Chromium.
- Ao mudar estrutura de macros ou eventos, atualize constantes, renderizacao, leitura, escrita, recarregamento, salvamento e autocomplete no editor.
- Preserve a edicao direta dos arquivos `.txt` da pasta `MACROS`.

## Politica de Limpeza de Arquivos

Pode sugerir remover backups, logs e copias paralelas que nao sao usados pelo firmware/editor, como `code_bkp.py`, `boot_out.txt`, `..MACROS/` ou `Nova pasta/`, desde que o usuario confirme que nao precisa preservar conteudo.

Nao sugira remover:

- `code.py`
- `boot.py`
- `MacroPlayEditor.html`
- `lib/`
- `MACROS/`
- Arquivos placeholder esperados dentro de `MACROS/`

## Como Evoluir Features

Ao implementar uma feature nova, identifique qual camada muda:

1. Firmware: leitura de hardware, execucao de eventos, sandbox de macros ou gerenciamento de memoria.
2. Boot: criacao idempotente de novas pastas/arquivos obrigatorios.
3. Editor: interface para visualizar, editar e salvar a nova configuracao.
4. Macros: exemplos ou templates de uso.
5. Documentacao: descricao do comportamento e cuidados para o usuario.

Se a feature cria novo evento, perfil, tecla, API de macro ou arquivo obrigatorio, atualize todas as camadas afetadas na mesma alteracao.

## Validacao Recomendada

Antes de finalizar alteracoes:

- Verifique se `boot.py` ainda cria todos os placeholders necessarios sem sobrescrever macros existentes.
- Verifique se `code.py` carrega apenas eventos existentes e ignora scripts vazios sem erro.
- Verifique se `MacroPlayEditor.html` consegue ler e salvar a mesma estrutura que o firmware usa.
- Procure erros de nome entre `keyboard` e `keyBoard`, `led` e `LED`, porque CircuitPython diferencia maiusculas/minusculas.
- Quando possivel, teste na placa ou revise considerando limitacoes reais do RP2040/CircuitPython.

## Estilo de Alteracao

- Prefira mudancas pequenas e focadas.
- Preserve nomes e padroes ja existentes quando eles fazem parte da interface com o usuario.
- Nao apague macros do usuario automaticamente.
- Escreva documentacao e comentarios em portugues quando forem voltados ao usuario do projeto.
- Explique riscos quando uma mudanca puder enviar teclas HID, prender uma tecla pressionada ou travar o loop principal.
