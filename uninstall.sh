#!/usr/bin/env bash
set -e

APP_DIR="$HOME/.local/share/controlarTeclado"
DESKTOP_FILE="$HOME/.local/share/applications/controlar-teclado.desktop"

echo "Removendo arquivos da aplicação..."
if [ -d "$APP_DIR" ]; then
    rm -rf "$APP_DIR"
    echo "Diretório $APP_DIR removido."
else
    echo "Diretório da aplicação não encontrado."
fi

echo "Removendo atalho do menu de aplicativos..."
if [ -f "$DESKTOP_FILE" ]; then
    rm -f "$DESKTOP_FILE"
    echo "Atalho $DESKTOP_FILE removido."
else
    echo "Atalho não encontrado."
fi

# Atualiza o cache de aplicativos do ambiente gráfico (se disponível)
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications"
fi

echo "Desinstalação concluída com sucesso!"
