#!/usr/bin/env bash
# =============================================================
# Deploy Script — reflow.mci → Hostinger KVM4
# Executa via: bash deploy.sh
# Pré-requisito: chave SSH configurada para o servidor
# =============================================================

set -e  # Para em caso de erro

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÃO — editar antes de executar
# ─────────────────────────────────────────────────────────────
SSH_USER="SEU_USUARIO_AQUI"        # Ex: u123456789 (ver painel Hostinger)
SSH_HOST="oficina.reflowmci.cloud"
REMOTE_DIR="~/public_html"          # Confirmar com: ssh usuario@host "echo ~"
LOCAL_DIR="."                        # Executar a partir do diretório reflow-mci-fixed/
# ─────────────────────────────────────────────────────────────

SSH="${SSH_USER}@${SSH_HOST}"

echo "=== Deploy: ${SSH} → ${REMOTE_DIR} ==="
echo ""

# PASSO 1 — Verificar conexão e caminho real
echo "[1/7] Verificando conexão SSH..."
ssh "$SSH" "echo 'Conexão OK. Home: ~. Caminho real: $(pwd)'"
echo ""

# PASSO 2 — Backup do site atual
echo "[2/7] Criando backup do site atual..."
ssh "$SSH" "tar -czf ~/backup-reflow-$(date +%Y%m%d-%H%M).tar.gz ${REMOTE_DIR}/ && echo 'Backup OK'"
echo ""

# PASSO 3 — Upload dos arquivos críticos
echo "[3/7] Fazendo upload dos arquivos críticos..."
scp "${LOCAL_DIR}/index.html"    "${SSH}:${REMOTE_DIR}/"
scp "${LOCAL_DIR}/styles.css"    "${SSH}:${REMOTE_DIR}/"
scp "${LOCAL_DIR}/favicon.svg"   "${SSH}:${REMOTE_DIR}/"
scp "${LOCAL_DIR}/manifest.json" "${SSH}:${REMOTE_DIR}/"
echo "Upload críticos OK"
echo ""

# PASSO 4 — .htaccess (com verificação prévia)
echo "[4/7] Verificando .htaccess existente no servidor..."
HTACCESS_EXISTS=$(ssh "$SSH" "test -f ${REMOTE_DIR}/.htaccess && echo 'exists' || echo 'new'")

if [ "$HTACCESS_EXISTS" = "exists" ]; then
  echo "ATENÇÃO: .htaccess já existe no servidor. Conteúdo atual:"
  ssh "$SSH" "cat ${REMOTE_DIR}/.htaccess"
  echo ""
  read -p "Substituir .htaccess? (s/n): " CONFIRM
  if [ "$CONFIRM" = "s" ] || [ "$CONFIRM" = "S" ]; then
    scp "${LOCAL_DIR}/.htaccess" "${SSH}:${REMOTE_DIR}/"
    echo ".htaccess substituído"
  else
    echo ".htaccess mantido. Mesclar manualmente se necessário."
  fi
else
  scp "${LOCAL_DIR}/.htaccess" "${SSH}:${REMOTE_DIR}/"
  echo ".htaccess criado"
fi
echo ""

# PASSO 5 — Template Pandoc e CSS de documento
echo "[5/7] Fazendo upload do sistema Pandoc..."
ssh "$SSH" "mkdir -p ${REMOTE_DIR}/_templates"
scp "${LOCAL_DIR}/pandoc-template.html"  "${SSH}:${REMOTE_DIR}/_templates/"
scp "${LOCAL_DIR}/styles-document.css"   "${SSH}:${REMOTE_DIR}/"
echo "Template Pandoc OK"
echo ""

# PASSO 6 — Permissões
echo "[6/7] Ajustando permissões..."
ssh "$SSH" "chmod 644 \
  ${REMOTE_DIR}/index.html \
  ${REMOTE_DIR}/styles.css \
  ${REMOTE_DIR}/styles-document.css \
  ${REMOTE_DIR}/favicon.svg \
  ${REMOTE_DIR}/manifest.json \
  ${REMOTE_DIR}/.htaccess \
  ${REMOTE_DIR}/_templates/pandoc-template.html"
echo "Permissões OK"
echo ""

# PASSO 7 — Verificação rápida via curl
echo "[7/7] Verificando arquivos acessíveis..."
echo ""
echo "--- styles.css (deve retornar 200 + Cache-Control) ---"
curl -si "https://${SSH_HOST}/styles.css" | head -10
echo ""
echo "--- favicon.svg (deve retornar 200) ---"
curl -si "https://${SSH_HOST}/favicon.svg" | head -5
echo ""
echo "--- manifest.json (deve retornar 200) ---"
curl -si "https://${SSH_HOST}/manifest.json" | head -5
echo ""

echo "=== Deploy concluído com sucesso! ==="
echo ""
echo "Próximos passos manuais:"
echo "  1. Abrir https://${SSH_HOST}/ no browser"
echo "  2. DevTools → Lighthouse → Gerar relatório"
echo "  3. Verificar Console (deve ter zero erros)"
echo "  4. Network tab → segundo reload → styles.css deve vir de cache"
