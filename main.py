from pathlib import Path
import sys
import json
import tkinter.colorchooser as colorchooser
import customtkinter as ctk

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

CORES_RAPIDAS = (
    "#FF2D55",
    "#FF9500",
    "#FFCC00",
    "#34C759",
    "#00C7BE",
    "#007AFF",
    "#AF52DE",
    "#FFFFFF",
)

BRILHO_LABELS = ("Off", "Low", "Med", "High")
MODO_LABELS = ("Estático", "Respiração")


def executarArgs(parametroName, argumentos, funcao):
    if parametroName in argumentos:
        parametroIndex = argumentos.index(parametroName)
        parametroValor = int(argumentos[parametroIndex + 1])
        print(parametroValor)
        funcao(parametroValor)


def ajusteBrilho(nivelBrilho):
    nivelBrilho = int(nivelBrilho)
    if nivelBrilho not in [0, 1, 2, 3]:
        raise ValueError("Escolha um brilho válido [0, 1, 2, 3]")
    pathBrilho.write_text(str(nivelBrilho))


def ajustarCor(**kwargs):
    comando = kwargs.get("comando", 1)
    modo = kwargs.get("modo", 0)
    corR = kwargs.get("red", 0)
    corG = kwargs.get("green", 0)
    corB = kwargs.get("blue", 0)
    velocidade = kwargs.get("velocidade", 1)
    comando = f"{str(comando)} {str(modo)} {str(corR)} {str(corG)} {str(corB)} {str(velocidade)}"
    pathCor.write_text(comando)
    print(comando)


def hex_para_rgb(hex_cor):
    hex_cor = hex_cor.lstrip("#")
    r = int(hex_cor[0:2], 16)
    g = int(hex_cor[2:4], 16)
    b = int(hex_cor[4:6], 16)
    return (r, g, b)


def carregar_config():
    if ARQUIVO_CONFIG.exists():
        config_text = ARQUIVO_CONFIG.read_text(encoding="UTF-8")
        return json.loads(config_text)
    return {"BRILHO": 3, "COR": "#d909d9", "MODO": 0}


def definir_config(config):
    r, g, b = hex_para_rgb(config.get("COR"))
    ajustarCor(red=r, green=g, blue=b, modo=int(config.get("MODO", 0)))
    ajusteBrilho(config.get("BRILHO"))


def salvar_config(config):
    ARQUIVO_CONFIG.write_text(json.dumps(config), encoding="UTF-8")


class App(ctk.CTk):
    BG = "#0B0D12"
    SURFACE = "#151821"
    SURFACE_2 = "#1C2030"
    BORDER = "#2A3145"
    TEXT = "#F4F6FB"
    MUTED = "#8B93A7"
    ACCENT = "#7C5CFF"

    def __init__(self, config):
        super().__init__()
        self.config_data = config
        self.cor_atual = (config.get("COR") or "#AF52DE").upper()
        self.brilho = int(config.get("BRILHO", 3))
        self.modo = int(config.get("MODO", 0))

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("ASUS Keyboard")
        self.geometry("720x980")
        self.minsize(640, 900)
        self.configure(fg_color=self.BG)

        self._build_ui()
        self._atualizar_preview(self.cor_atual)

    def _build_ui(self):
        root = ctk.CTkFrame(self, fg_color=self.BG)
        root.pack(fill="both", expand=True, padx=40, pady=36)

        # Header
        ctk.CTkLabel(
            root,
            text="ASUS RGB",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=self.ACCENT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            root,
            text="Controle do teclado",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=self.TEXT,
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            root,
            text="Brilho, cor e efeito em um só lugar.",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color=self.MUTED,
        ).pack(anchor="w", pady=(6, 28))

        # Preview card
        preview_card = ctk.CTkFrame(
            root, fg_color=self.SURFACE, corner_radius=26, border_width=1, border_color=self.BORDER
        )
        preview_card.pack(fill="x", pady=(0, 22))

        preview_inner = ctk.CTkFrame(preview_card, fg_color="transparent")
        preview_inner.pack(fill="x", padx=28, pady=28)

        self.glow = ctk.CTkFrame(
            preview_inner, width=120, height=120, corner_radius=60, fg_color=self.cor_atual
        )
        self.glow.pack(side="left")
        self.glow.pack_propagate(False)

        self.glow_core = ctk.CTkFrame(
            self.glow, width=72, height=72, corner_radius=36, fg_color="#FFFFFF"
        )
        self.glow_core.place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(preview_inner, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=(24, 0))

        ctk.CTkLabel(
            info,
            text="Cor ativa",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=self.MUTED,
        ).pack(anchor="w")

        self.label_hex = ctk.CTkLabel(
            info,
            text=self.cor_atual,
            font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
            text_color=self.TEXT,
        )
        self.label_hex.pack(anchor="w", pady=(4, 14))

        ctk.CTkButton(
            info,
            text="Escolher cor",
            width=140,
            height=42,
            corner_radius=12,
            fg_color=self.SURFACE_2,
            hover_color=self.BORDER,
            border_width=1,
            border_color=self.BORDER,
            text_color=self.TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._escolher_cor,
        ).pack(anchor="w")

        # Quick colors
        self._secao(root, "Paleta rápida")
        palette = ctk.CTkFrame(root, fg_color="transparent")
        palette.pack(fill="x", pady=(10, 24))

        for i, cor in enumerate(CORES_RAPIDAS):
            btn = ctk.CTkButton(
                palette,
                text="",
                width=52,
                height=52,
                corner_radius=26,
                fg_color=cor,
                hover_color=cor,
                border_width=3,
                border_color="#FFFFFF" if cor.upper() == self.cor_atual.upper() else self.SURFACE,
                command=lambda c=cor: self._aplicar_cor(c),
            )
            btn.grid(row=0, column=i, padx=6)
            if not hasattr(self, "palette_btns"):
                self.palette_btns = []
            self.palette_btns.append((btn, cor))

        # Brightness
        self._secao(root, "Brilho")
        self.seg_brilho = ctk.CTkSegmentedButton(
            root,
            values=list(BRILHO_LABELS),
            command=self._on_brilho,
            height=48,
            corner_radius=14,
            border_width=0,
            selected_color=self.ACCENT,
            selected_hover_color="#6A4AE8",
            unselected_color=self.SURFACE,
            unselected_hover_color=self.SURFACE_2,
            text_color=self.TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
        )
        self.seg_brilho.set(BRILHO_LABELS[self.brilho])
        self.seg_brilho.pack(fill="x", pady=(10, 24))

        # Effect
        self._secao(root, "Efeito")
        self.seg_modo = ctk.CTkSegmentedButton(
            root,
            values=list(MODO_LABELS),
            command=self._on_modo,
            height=48,
            corner_radius=14,
            border_width=0,
            selected_color=self.ACCENT,
            selected_hover_color="#6A4AE8",
            unselected_color=self.SURFACE,
            unselected_hover_color=self.SURFACE_2,
            text_color=self.TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
        )
        self.seg_modo.set(MODO_LABELS[self.modo if self.modo in (0, 1) else 0])
        self.seg_modo.pack(fill="x", pady=(10, 24))

        # Hex input
        self._secao(root, "Hex manual")
        hex_row = ctk.CTkFrame(root, fg_color="transparent")
        hex_row.pack(fill="x", pady=(10, 0))

        self.entrada_cor = ctk.CTkEntry(
            hex_row,
            height=48,
            corner_radius=14,
            border_width=1,
            border_color=self.BORDER,
            fg_color=self.SURFACE,
            text_color=self.TEXT,
            placeholder_text="#RRGGBB",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            justify="center",
        )
        self.entrada_cor.insert(0, self.cor_atual)
        self.entrada_cor.pack(side="left", fill="x", expand=True)
        self.entrada_cor.bind("<Return>", self._on_cor_digitada)
        self.entrada_cor.bind("<FocusOut>", self._on_cor_digitada)

        ctk.CTkButton(
            hex_row,
            text="Aplicar",
            width=120,
            height=48,
            corner_radius=14,
            fg_color=self.ACCENT,
            hover_color="#6A4AE8",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            command=lambda: self._on_cor_digitada(),
        ).pack(side="left", padx=(12, 0))

        # Footer
        footer = ctk.CTkFrame(root, fg_color="transparent")
        footer.pack(fill="x", side="bottom", pady=(36, 0))

        ctk.CTkLabel(
            footer,
            text="Alterações salvas automaticamente",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.MUTED,
        ).pack(side="left")

        ctk.CTkButton(
            footer,
            text="Sair",
            width=100,
            height=40,
            corner_radius=12,
            fg_color="transparent",
            hover_color=self.SURFACE_2,
            border_width=1,
            border_color=self.BORDER,
            text_color=self.TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            command=self._sair,
        ).pack(side="right")

    def _secao(self, parent, titulo):
        ctk.CTkLabel(
            parent,
            text=titulo.upper(),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.MUTED,
        ).pack(anchor="w")

    def _atualizar_preview(self, hex_cor):
        self.glow.configure(fg_color=hex_cor)
        self.label_hex.configure(text=hex_cor.upper())
        for btn, cor in self.palette_btns:
            selecionada = cor.upper() == hex_cor.upper()
            btn.configure(border_color="#FFFFFF" if selecionada else self.SURFACE)

    def _aplicar_cor(self, hex_cor, modo=None):
        hex_cor = hex_cor.strip().upper()
        if not hex_cor.startswith("#"):
            hex_cor = f"#{hex_cor}"
        if len(hex_cor) != 7:
            return
        try:
            r, g, b = hex_para_rgb(hex_cor)
        except ValueError:
            return

        if modo is None:
            modo = self.modo

        ajustarCor(red=r, green=g, blue=b, modo=modo)
        self.cor_atual = hex_cor
        self.modo = modo
        self.config_data["COR"] = hex_cor
        self.config_data["MODO"] = modo
        self.entrada_cor.delete(0, "end")
        self.entrada_cor.insert(0, hex_cor)
        self._atualizar_preview(hex_cor)
        salvar_config(self.config_data)

    def _on_brilho(self, valor):
        nivel = BRILHO_LABELS.index(valor)
        self.brilho = nivel
        ajusteBrilho(nivel)
        self.config_data["BRILHO"] = nivel
        salvar_config(self.config_data)

    def _on_modo(self, valor):
        modo = MODO_LABELS.index(valor)
        self.modo = modo
        self._aplicar_cor(self.cor_atual, modo=modo)

    def _on_cor_digitada(self, _event=None):
        self._aplicar_cor(self.entrada_cor.get())

    def _escolher_cor(self):
        cor = colorchooser.askcolor(
            color=self.cor_atual, title="Escolher cor do LED", parent=self
        )
        if cor and cor[1]:
            self._aplicar_cor(cor[1])

    def _sair(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Tchau")
        popup.geometry("260x150")
        popup.resizable(False, False)
        popup.configure(fg_color=self.BG)
        popup.transient(self)
        popup.grab_set()

        card = ctk.CTkFrame(
            popup, fg_color=self.SURFACE, corner_radius=18, border_width=1, border_color=self.BORDER
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            card,
            text="Asus VTNC!",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=self.TEXT,
        ).pack(pady=(22, 12))

        ctk.CTkButton(
            card,
            text="OK",
            width=90,
            height=34,
            corner_radius=10,
            fg_color=self.ACCENT,
            hover_color="#6A4AE8",
            command=self.destroy,
        ).pack(pady=(0, 18))


if __name__ == "__main__":
    args = sys.argv
    print(pathBrilho.read_text())
    executarArgs("--brilho", args, ajusteBrilho)
    config = carregar_config()
    definir_config(config=config)

    app = App(config)
    app.mainloop()
