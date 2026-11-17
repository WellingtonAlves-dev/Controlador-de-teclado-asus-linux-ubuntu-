from pathlib import Path
import sys
import PySimpleGUI as sg
import json

'''
A estrutura esperada pelo driver segue a ordem:comando modo vermelho verde azul velocidade

Comandos: 1 (aplicar imediatamente) ou 2 (salvar na memória do teclado).

Modos: 0 (Estático), 1 (Respiração/Breathing), 2 (Ciclo de Cores), 3 (Arco-íris / Strobing).

Cores (R, G, B): Valores inteiros de 0 a 255.

Velocidade: 0 (lenta), 1 (média) ou 2 (rápida).

Exemplos práticos:

echo "1 0 0 255 255 0" | sudo tee /sys/class/leds/asus::kbd_backlight/kbd_rgb_mode

'''

PASTA_ATUAL = Path(__file__).parent
ARQUIVO_CONFIG = PASTA_ATUAL / "config.json"
CAMINHO_BRILHO = "/sys/class/leds/asus::kbd_backlight/brightness"
CAMINHO_CORES = "/sys/class/leds/asus::kbd_backlight/kbd_rgb_mode"
pathBrilho = Path(CAMINHO_BRILHO)
pathCor = Path(CAMINHO_CORES)




def executarArgs(parametroName, argumentos, funcao):
    if parametroName in argumentos:
        parametroIndex = argumentos.index(parametroName)
        parametroValor = int(argumentos[parametroIndex + 1])
        print(parametroValor)
        funcao(parametroValor)

def ajusteBrilho(nivelBrilho):
    nivelBrilho = int(nivelBrilho)
    if(nivelBrilho not in [0, 1, 2, 3]):
        raise("Escolha um brilho válido [0, 1, 2, 3]")
    pathBrilho.write_text(str(nivelBrilho))

def ajustarCor(**kwargs):
    comando = kwargs.get("comando", 1)
    modo = kwargs.get("modo", 0) # 0 = estatico, 1 = respiração, 2 = ciclo, 3 = arco iris
    corR = kwargs.get("red", 0)
    corG = kwargs.get("green", 0)
    corB = kwargs.get("blue", 0)
    velocidade = kwargs.get("velocidade", 1) # 0 = lenta, 1 = média, 2 = rápida
    comando = f"{str(comando)} {str(modo)} {str(corR)} {str(corG)} {str(corB)} {str(velocidade)}"
    pathCor.write_text(comando)
    print(comando)

def hex_para_rgb(hex_cor):
    # Remove o '#' se estiver presente
    hex_cor = hex_cor.lstrip('#')
    
    # Converte cada par de caracteres de hexadecimal (base 16) para inteiro
    r = int(hex_cor[0:2], 16)
    g = int(hex_cor[2:4], 16)
    b = int(hex_cor[4:6], 16)
    
    return (r, g, b)

def carregar_config():
    if(ARQUIVO_CONFIG.exists()):
        config_text = ARQUIVO_CONFIG.read_text(encoding="UTF-8")
        config_json = json.loads(config_text)
        return config_json
    return {
        "BRILHO": "3",
        "COR": "#d909d9",
        "MODO": 0
    }

def definir_config(config):
    r, g, b = hex_para_rgb(config.get("COR"))
    ajustarCor(red=r, green=g, blue=b)

    brilho = config.get("BRILHO")
    ajusteBrilho(brilho)

def salvar_config(config):
    ARQUIVO_CONFIG.write_text(json.dumps(config), encoding="UTF-8")

if __name__ == "__main__":
    args = sys.argv
    print(pathBrilho.read_text())
    # BRILHO
    executarArgs("--brilho", args, ajusteBrilho)
    config = carregar_config()
    #ajustarCor(red=0, green=255, blue=255)
    # 1. Escolha um tema moderno antes de criar o layout
    sg.theme("DarkGrey13")  # Outras boas opções: "DarkTeal9", "DarkBlue3", "Black"

    # Configuração padrão de fontes e espaçamentos
    FONTE_TITULO = ("Segoe UI", 14, "bold")
    FONTE_NORMAL = ("Segoe UI", 10)
    cor_atual = config.get("COR") or "#00FF00"  # Fallback caso venha vazio
    layout = [
        # Cabeçalho para dar identidade ao app
        [sg.Text("⌨️ Controle RGB do Teclado", font=FONTE_TITULO, pad=((0, 0), (5, 15)))],
        # Frame de Brilho
        [
            sg.Frame(
                " Brilho ",
                [
                    [
                        sg.Radio(
                            "Desligado",
                            group_id="BRILHO",
                            key="-BRILHO-DESLIGADO-",
                            default=config.get("BRILHO") == "0",
                            enable_events=True,
                            pad=(10, 8),
                        ),
                        sg.Radio(
                            "Baixo",
                            group_id="BRILHO",
                            key="-BRILHO-BAIXO-",
                            default=config.get("BRILHO") == "1",
                            enable_events=True,
                            pad=(10, 8),
                        ),
                        sg.Radio(
                            "Médio",
                            group_id="BRILHO",
                            key="-BRILHO-MEDIO-",
                            default=config.get("BRILHO") == "2",
                            enable_events=True,
                            pad=(10, 8),
                        ),
                        sg.Radio(
                            "Alto",
                            group_id="BRILHO",
                            key="-BRILHO-ALTO-",
                            default=config.get("BRILHO") == "3",
                            enable_events=True,
                            pad=(10, 8),
                        ),
                    ]
                ],
                expand_x=True,
                pad=(0, 8),
                relief=sg.RELIEF_GROOVE,
            )
        ],
        # Frame de Cor + Modo lado a lado para aproveitar melhor o espaço horizontal
        [
            sg.Frame(
                " Cor do LED ",
                [
                    [
                        # Quadradinho que mostra o preview da cor selecionada
                        sg.Text(
                            "   ",
                            key="-PREVIEW-COR-",
                            background_color=cor_atual,
                            relief=sg.RELIEF_SOLID,
                            pad=((10, 5), 10),
                        ),
                        sg.Input(
                            key="-COR-",
                            size=(10, 1),
                            enable_events=True,
                            default_text=cor_atual,
                            justification="center",
                        ),
                        sg.ColorChooserButton(
                            "🎨 Alterar", target="-COR-", pad=((5, 10), 10)
                        ),
                    ]
                ],
                expand_x=True,
                pad=((0, 5), 8),
                relief=sg.RELIEF_GROOVE,
            ),
            sg.Frame(
                " Efeito ",
                [
                    [
                        sg.Radio(
                            "Estático",
                            group_id="MODO",
                            key="-ESTATICO-",
                            default=config.get("MODO") == "0",
                            enable_events=True,
                            pad=(10, 10),
                        ),
                        sg.Radio(
                            "Respiração",
                            group_id="MODO",
                            key="-RESPIRACAO-",
                            default=config.get("MODO") == "1",
                            enable_events=True,
                            pad=(10, 10),
                        ),
                    ]
                ],
                expand_x=True,
                pad=((5, 0), 8),
                relief=sg.RELIEF_GROOVE,
            ),
        ],
        # Linha divisória sutil e botão Sair alinhado à direita
        [sg.HorizontalSeparator(pad=(0, 12))],
        [
            sg.Push(),
            sg.Button(
                "Sair",
                key="SAIR",
                size=(10, 1),
                button_color=("white", "#C0392B"),
                pad=(0, 5),
            ),
        ],
    ]

    # Na criação da janela, adicione margens externas (margins) e a fonte padrão:
    window = sg.Window(
        "Configuração do Teclado",
        layout,
        font=FONTE_NORMAL,
        margins=(20, 15),
        finalize=True,
    )
    definir_config(config=config)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '-BRILHO-DESLIGADO-':
            ajusteBrilho(0) 
            config["BRILHO"] = 0
            salvar_config(config)

        if event == "-BRILHO-BAIXO-":
            ajusteBrilho(1)
            config["BRILHO"] = 1
            salvar_config(config)
        if event == "-BRILHO-MEDIO-":
            ajusteBrilho(2)
            config["BRILHO"] = 2
            salvar_config(config)
        if event == "-BRILHO-ALTO-":
            ajusteBrilho(3)
            config["BRILHO"] = 3
            salvar_config(config)
        if event == "-COR-":
            hexCor = values["-COR-"]
            r, g, b = hex_para_rgb(hexCor)
            ajustarCor(red=r, green=g, blue=b)
            config["COR"] = hexCor
            salvar_config(config)

        if event == "-ESTATICO-":
            config["MODO"] = 0
            hexCor = values["-COR-"]
            r, g, b = hex_para_rgb(hexCor)
            ajustarCor(red=r, green=g, blue=b, modo=0)
            config["COR"] = hexCor

            salvar_config(config)
        if event == "-RESPIRACAO-":
            config["MODO"] = 1
            hexCor = values["-COR-"]
            r, g, b = hex_para_rgb(hexCor)
            ajustarCor(red=r, green=g, blue=b, modo=1)
            config["COR"] = hexCor

            salvar_config(config)

            
        if event == "SAIR":
            #Nós não usou IA, comédia!. Att, usei IA ;-;, mas para me ajudar a estilizar e fazer o install.sh
            sg.popup(title="Tchau", custom_text="Asus VTNC!")
            break

    window.close()
