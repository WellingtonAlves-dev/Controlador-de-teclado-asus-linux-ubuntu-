#!/usr/bin/env bash
set -e

APP_DIR="$HOME/.local/share/controlarTeclado"
DESKTOP_FILE="$HOME/.local/share/applications/controlar-teclado.desktop"

echo "Instalando dependências do sistema (python3-venv e python3-tk)..."
sudo apt update && sudo apt install -y python3-venv python3-tk

echo "Copiando arquivos do projeto para $APP_DIR..."
mkdir -p "$APP_DIR"
cp main.py config.json requirements.txt ControlaTecladoAsus.jpeg "$APP_DIR/"

echo "Criando ambiente virtual e instalando bibliotecas..."
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "Criando atalho no menu de aplicativos..."
mkdir -p "$HOME/.local/share/applications"
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name=Controlador de Teclado ASUS
Comment=Controle de brilho e RGB do teclado
Exec=$APP_DIR/venv/bin/python $APP_DIR/main.py
Icon=$APP_DIR/ControlaTecladoAsus.jpeg
Terminal=false
Type=Application
Categories=Utility;Settings;
EOF

chmod +x "$DESKTOP_FILE"

echo "Instalação concluída!"
