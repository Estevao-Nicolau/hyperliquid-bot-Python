#!/bin/bash

#######################################################################
#  🤖 RODAR BOT HYPERLIQUID - SCRIPT INTERATIVO
#######################################################################

set -e

BASE_DIR="/Users/nicolaudev/hyperliquid-trading-bot"
cd "$BASE_DIR"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🤖 HYPERLIQUID TRADING BOT LAUNCHER              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "❌ .env não encontrado!"
    echo ""
    echo "Copie o template:"
    echo "  cp .env.example .env"
    echo ""
    echo "Edite com suas credenciais Hyperliquid:"
    echo "  nano .env"
    echo ""
    exit 1
fi

# Menu de opções
echo "Escolha como rodar:"
echo ""
echo "1) 📋 Validar configuração (sem rodar)"
echo "2) 📊 Paper Trading (simulado, sem risco)"
echo "3) 🧪 Testnet (com API de teste)"
echo "4) 💰 Mainnet (DINHEIRO REAL - ⚠️  cuidado!)"
echo "5) ⚙️  Versão específica (escolher config)"
echo "6) ❌ Sair"
echo ""
read -p "Escolha (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🔍 Validando configuração..."
        python3 src/run_bot.py --validate
        ;;
    2)
        echo ""
        echo "📊 Iniciando Paper Trading (modo simulado)..."
        echo "   ℹ️  Nenhuma ordem real será executada"
        echo "   💾 Usando exchange simulada"
        echo "   ⏱️  Pressione Ctrl+C para parar"
        echo ""
        python3 src/run_bot.py --paper
        ;;
    3)
        echo ""
        echo "🧪 Iniciando em TESTNET..."
        echo "   ⚠️  Verifique que .env tem HYPERLIQUID_TESTNET=true"
        echo "   ⏱️  Pressione Ctrl+C para parar"
        echo ""
        python3 src/run_bot.py
        ;;
    4)
        echo ""
        echo "⚠️  ⚠️  ⚠️  MODO MAINNET - DINHEIRO REAL ⚠️  ⚠️  ⚠️"
        echo ""
        echo "Confirmações:"
        echo "  1. Você testou em paper trading? (S/N)"
        read -p "    Resposta: " test_paper
        
        echo "  2. Você testou em testnet? (S/N)"
        read -p "    Resposta: " test_testnet
        
        echo "  3. Você tem backup do .env? (S/N)"
        read -p "    Resposta: " has_backup
        
        echo "  4. Você sabe pressionar Ctrl+C para parar? (S/N)"
        read -p "    Resposta: " knows_stop
        
        if [ "$test_paper" = "S" ] || [ "$test_paper" = "s" ]; then
            if [ "$test_testnet" = "S" ] || [ "$test_testnet" = "s" ]; then
                if [ "$has_backup" = "S" ] || [ "$has_backup" = "s" ]; then
                    if [ "$knows_stop" = "S" ] || [ "$knows_stop" = "s" ]; then
                        echo ""
                        echo "✅ Tudo confirmado!"
                        echo "🚀 Iniciando em MAINNET (DINHEIRO REAL)..."
                        echo "   ⏱️  Pressione Ctrl+C para parar"
                        echo ""
                        python3 src/run_bot.py
                    else
                        echo "❌ Você precisa saber parar o bot (Ctrl+C)"
                        exit 1
                    fi
                else
                    echo "❌ Sempre tenha backup do .env"
                    exit 1
                fi
            else
                echo "❌ Teste em testnet primeiro!"
                exit 1
            fi
        else
            echo "❌ Teste em paper trading primeiro!"
            exit 1
        fi
        ;;
    5)
        echo ""
        echo "📁 Configs disponíveis:"
        ls -1 bots/*.yaml | nl
        echo ""
        read -p "Escolha (número): " config_num
        config=$(ls -1 bots/*.yaml | sed -n "${config_num}p")
        
        if [ -z "$config" ]; then
            echo "❌ Config inválida"
            exit 1
        fi
        
        echo ""
        echo "Modo:"
        echo "  1) Validar"
        echo "  2) Paper Trading"
        echo "  3) Rodar"
        read -p "Escolha (1-3): " mode
        
        if [ "$mode" = "1" ]; then
            python3 src/run_bot.py --config "$config" --validate
        elif [ "$mode" = "2" ]; then
            python3 src/run_bot.py --config "$config" --paper
        elif [ "$mode" = "3" ]; then
            echo "🚀 Iniciando com config: $config"
            python3 src/run_bot.py --config "$config"
        fi
        ;;
    6)
        echo "👋 Até logo!"
        exit 0
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "✅ Bot finalizado"
echo ""
