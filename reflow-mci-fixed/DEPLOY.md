# Guia de Deploy - Portal SMS Extrema/MG

## 📋 Pré-requisitos

- Acesso FTP/SFTP ao servidor Hostinger (KVM4)
- Cliente FTP (FileZilla, WinSCP, ou similar)
- Backup do site atual (recomendado)

---

## 🚀 Passos de Deploy

### 1. Backup do Site Atual

**IMPORTANTE:** Antes de fazer qualquer alteração, faça backup completo:

```bash
# Via FTP, baixar todos os arquivos para:
backup-reflow-mci-YYYY-MM-DD/
```

### 2. Upload dos Arquivos Corrigidos

Fazer upload dos seguintes arquivos para o diretório raiz do site:

| Arquivo | Destino | Ação |
|---------|---------|------|
| `index.html` | `/index.html` | **SUBSTITUIR** |
| `styles.css` | `/styles.css` | **CRIAR** (novo) |
| `manifest.json` | `/manifest.json` | **CRIAR** (novo) |
| `favicon.svg` | `/favicon.svg` | **CRIAR** (novo) |
| `.htaccess` | `/.htaccess` | **CRIAR ou MESCLAR** (*) |

**(*) Importante:** Se já existe um arquivo `.htaccess`, **não substitua cegamente**. Abra o existente e adicione as regras do novo `.htaccess` sem sobrescrever configurações críticas (como redirects ou regras de rewrite).

### 3. Criar Ícones PWA (Opcional mas Recomendado)

O `manifest.json` referencia ícones PNG que precisam ser criados:

**Opção A: Usar ferramenta online (recomendado)**
1. Acesse: https://realfavicongenerator.net/
2. Upload do `favicon.svg`
3. Gerar pacote completo de ícones
4. Baixar e fazer upload dos arquivos:
   - `icon-192.png` → `/icon-192.png`
   - `icon-512.png` → `/icon-512.png`
   - `favicon-32x32.png` → `/favicon-32x32.png`
   - `favicon-16x16.png` → `/favicon-16x16.png`
   - `apple-touch-icon.png` → `/apple-touch-icon.png`

**Opção B: Comandos ImageMagick (se tiver acesso SSH)**
```bash
# Gerar PNG a partir do SVG
convert favicon.svg -resize 192x192 icon-192.png
convert favicon.svg -resize 512x512 icon-512.png
convert favicon.svg -resize 32x32 favicon-32x32.png
convert favicon.svg -resize 16x16 favicon-16x16.png
convert favicon.svg -resize 180x180 apple-touch-icon.png
```

### 4. Criar Open Graph Image (Opcional)

Para melhor compartilhamento em redes sociais, crie uma imagem 1200x630px:

**Conteúdo sugerido:**
- Fundo: `#1a365d` (azul institucional)
- Texto: "Portal de Documentos - SMS Extrema/MG"
- Subtexto: "Contratações Públicas"
- Logo da prefeitura (se disponível)

Salvar como: `/og-image.png`

### 5. Verificar Permissões

Após upload, garantir permissões corretas:

```bash
# Arquivos: 644 (rw-r--r--)
chmod 644 index.html styles.css manifest.json *.png *.svg

# .htaccess: 644
chmod 644 .htaccess
```

### 6. Limpar Cache

**No servidor (se tiver acesso SSH):**
```bash
# Limpar cache do Apache (se mod_cache estiver ativo)
sudo service apache2 reload
```

**No navegador:**
1. Abrir DevTools (F12)
2. Network → Disable cache
3. Hard refresh (Ctrl+Shift+R)

---

## ✅ Checklist de Validação Pós-Deploy

### Funcionalidade Básica
- [ ] Site carrega corretamente
- [ ] CSS está sendo aplicado (verificar Network tab - `styles.css` deve retornar 200)
- [ ] Todos os 6 cards estão visíveis e clicáveis
- [ ] Links funcionam corretamente

### Responsividade
- [ ] Testar em mobile (375px): 1 coluna
- [ ] Testar em tablet (640px-899px): 2 colunas
- [ ] Testar em desktop (≥900px): 3 colunas
- [ ] Sem scroll horizontal em nenhum viewport

### Acessibilidade
- [ ] Emojis 🔒 têm `aria-label` (inspecionar com DevTools)
- [ ] Foco visível ao navegar com Tab
- [ ] Contraste de cores adequado (texto legível)

### SEO e Meta Tags
- [ ] Favicon aparece na aba do navegador
- [ ] Meta description presente (View Page Source)
- [ ] Open Graph tags presentes (testar com: https://www.opengraph.xyz/)

### Performance
- [ ] Lighthouse Performance ≥90 (DevTools → Lighthouse)
- [ ] CSS em cache (Network tab - segundo reload deve vir de cache)
- [ ] Sem erros no console

### PWA
- [ ] `manifest.json` acessível: https://oficina.reflowmci.cloud/manifest.json
- [ ] Chrome mostra opção "Instalar aplicativo" (ícone + na barra de endereço)

---

## 🛠️ Troubleshooting

### Problema: CSS não está sendo aplicado

**Sintomas:** Site aparece sem estilos (apenas texto plano)

**Soluções:**
1. Verificar se `styles.css` foi feito upload no diretório raiz
2. Verificar permissões do arquivo (deve ser 644)
3. Limpar cache do navegador (Ctrl+Shift+R)
4. Verificar Network tab: `styles.css` deve retornar status 200 (não 404)
5. Se usar versionamento (`?v=1.0.0`), garantir que o HTML tem a mesma versão

### Problema: Favicon não aparece

**Soluções:**
1. Fazer hard refresh (Ctrl+Shift+R)
2. Aguardar alguns minutos (navegadores cacheiam favicons agressivamente)
3. Testar em modo anônimo
4. Verificar se arquivo existe: https://oficina.reflowmci.cloud/favicon.svg
5. Verificar MIME type do servidor (deve ser `image/svg+xml`)

### Problema: Headers de cache não funcionam

**Sintomas:** Arquivos sempre baixam do servidor (nunca vêm de cache)

**Soluções:**
1. Verificar se `.htaccess` foi feito upload
2. Verificar se o Apache tem `mod_expires` e `mod_headers` habilitados
3. Checar logs do Apache para erros
4. Contactar suporte Hostinger para habilitar módulos

### Problema: Site está quebrado após deploy

**Ação imediata:**
1. Restaurar backup do `index.html` original
2. Remover `styles.css` temporariamente
3. Revisar arquivos antes de tentar novamente
4. Contactar suporte técnico se necessário

---

## 📊 Ferramentas de Validação

### Lighthouse (Chrome DevTools)
```
1. F12 → Lighthouse
2. Selecionar: Performance, Accessibility, Best Practices, SEO
3. Generate report
4. Target: Accessibility 100, SEO ≥95, Performance ≥90
```

### axe DevTools (Extensão)
```
1. Instalar: https://www.deque.com/axe/devtools/
2. F12 → axe DevTools
3. Scan All of My Page
4. Target: 0 violations
```

### WAVE (Web Accessibility Evaluation Tool)
```
URL: https://wave.webaim.org/
Input: https://oficina.reflowmci.cloud/
Target: 0 errors, 0 contrast errors
```

### WebAIM Contrast Checker
```
URL: https://webaim.org/resources/contrastchecker/
Verificar:
- #5a6c7d em #ffffff (texto secundário) → deve passar AAA
- #1a365d em #ffffff (títulos) → deve passar AAA
```

### Open Graph Debugger
```
Facebook: https://developers.facebook.com/tools/debug/
LinkedIn: https://www.linkedin.com/post-inspector/
Input: https://oficina.reflowmci.cloud/
```

### Manifest Validator
```
Chrome: DevTools → Application → Manifest
Verificar: sem erros, ícones carregando
```

---

## 📝 Notas Importantes

### Versionamento de Assets

O arquivo CSS está referenciado como `styles.css?v=1.0.0`. Ao fazer atualizações futuras:

1. Modificar `styles.css` no servidor
2. **Incrementar versão** no HTML: `styles.css?v=1.0.1`
3. Isso força navegadores a baixarem a nova versão (cache busting)

### HTTPS

Se o site ainda não usa HTTPS, **FORTEMENTE RECOMENDADO** habilitar:

1. Acessar painel Hostinger
2. SSL/TLS → Ativar Let's Encrypt (gratuito)
3. Descomentar linhas no `.htaccess` para forçar HTTPS

### Conformidade Legal

O portal serve documentos públicos sob Lei 14.133/2021. As melhorias de acessibilidade garantem conformidade com:
- Decreto 5.296/2004 (Acessibilidade em portais governamentais)
- eMAG - Modelo de Acessibilidade em Governo Eletrônico

---

## 🔄 Próximas Iterações (Roadmap Futuro)

### Curto Prazo (1-2 meses)
- [ ] Adicionar sistema de busca/filtro de documentos
- [ ] Implementar dark mode toggle
- [ ] Adicionar indicador de "Novo documento" (badge)

### Médio Prazo (3-6 meses)
- [ ] Sistema de notificações para novos uploads
- [ ] Exportação de listagem (CSV/PDF)
- [ ] Integração com Matomo Analytics (self-hosted)

### Longo Prazo (6-12 meses)
- [ ] Service Worker para offline-first (PWA completo)
- [ ] Sistema de autenticação para seções restritas
- [ ] API backend para gerenciamento dinâmico de documentos

---

## 📞 Suporte

Em caso de problemas durante o deploy:

1. **Backup:** Sempre manter backup acessível
2. **Reversão:** Restaurar versão anterior se algo quebrar
3. **Suporte Hostinger:** Contactar para questões de servidor
4. **Desenvolvedor:** Reportar bugs encontrados

---

**Versão:** 1.0.0
**Data:** 2026-02-15
**Autor:** Sistema de Assistência IA (Claude Sonnet 4.5)
**Projeto:** Portal SMS Extrema/MG - Modernização Frontend
