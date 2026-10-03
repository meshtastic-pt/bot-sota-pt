# 🇵🇹 Meshtastic Portugal Bot

Bot de integração para redes **Meshtastic em Portugal**, adaptado a partir do projeto original [bot-ea7](https://github.com/nandoraya/bot-ea7), desenvolvido por **nandoraya**.

O objetivo deste fork é manter a filosofia e as funcionalidades úteis do projeto original, mas adaptar a informação, geografia e fontes de dados à realidade portuguesa e à comunidade **Meshtastic Portugal**.

> **Estado:** fork em desenvolvimento / experimental.  
> A estrutura e os adaptadores portugueses estão preparados, mas algumas integrações externas — especialmente SOTA e dados estruturados de incêndios — devem ser validadas antes de utilização em produção.

---

## 🧭 Sobre o projeto original

Este projeto nasceu a partir do:

**[nandoraya/bot-ea7](https://github.com/nandoraya/bot-ea7)**

O `bot-ea7` é um bot orientado para redes Meshtastic que combina informação proveniente da mesh com serviços externos e disponibiliza essa informação através de **Meshtastic e Telegram**.

Entre as funcionalidades existentes na base original encontram-se:

- comunicação com nós Meshtastic;
- integração via interface Meshtastic;
- Telegram;
- MQTT;
- traceroute;
- informação de nós;
- QRZ / HamQTH;
- SOTA;
- informação meteorológica;
- alertas;
- sismos;
- incêndios;
- ferramentas de diagnóstico;
- integração com serviços de IA;
- armazenamento local em SQLite.

A arquitetura original foi particularmente pensada para a realidade da região espanhola EA7/Andaluzia, incluindo referências geográficas e fontes de informação específicas dessa zona.

Este fork mantém a base funcional sempre que ela é útil, mas remove as dependências específicas de Espanha.

---

# 🇵🇹 O que muda neste fork

A adaptação portuguesa segue quatro princípios:

### 1. Remover dependências geográficas espanholas

Foram removidos ou estão a ser removidos:

- províncias espanholas;
- referências específicas de Andaluzia;
- routers Meshtastic fixos definidos pelo administrador;
- AEMET;
- EMSC;
- INFOCA;
- NASA FIRMS como fonte principal de incêndios;
- funcionalidade de preços de gasolina.

O bot deixa de assumir que existe uma determinada infraestrutura fixa de routers.

---

### 2. Usar as regiões SOTA de Portugal

A geografia principal passa a ser baseada nas **regiões SOTA de Portugal continental**:

| Código | Região |
|---|---|
| `CT/AA` | Alto Alentejo |
| `CT/AL` | Algarve |
| `CT/BA` | Beira Alta |
| `CT/BB` | Beira Baixa |
| `CT/BL` | Beira Litoral |
| `CT/BT` | Baixo Alentejo |
| `CT/DL` | Douro Litoral |
| `CT/ES` | Estremadura |
| `CT/MN` | Minho |
| `CT/RB` | Ribatejo |
| `CT/TM` | Trás-os-Montes e Alto Douro |

Por exemplo:

```text
CT/AL-001
CT/BL-012
CT/BA-034
CT/TM-005
```

O parser português aceita também:

```text
AL-001
CT-AL-001
CT/AL-001
```

### Madeira e Açores

Nesta primeira fase o projeto concentra-se no **Portugal continental / CT**.

Ficam para uma fase posterior:

```text
CT3 → Madeira
CU  → Açores
```

Isto permite manter a lógica continental simples antes de acrescentar as particularidades dessas associações.

---

# 📡 Como funciona

A arquitetura geral é:

```text
                    ┌─────────────────┐
                    │     Telegram    │
                    └────────┬────────┘
                             │
                             │
┌──────────────┐      ┌──────▼──────┐      ┌───────────────┐
│ Meshtastic   │◄────►│     Bot     │◄────►│ MQTT / Mesh   │
│ nodes / mesh │      │             │      │ infrastructure│
└──────────────┘      └──────┬──────┘      └───────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
            IPMA           SOTA          SGIFR/ANEPC
```

O bot funciona como uma camada de integração.

A rede Meshtastic fornece a conectividade de baixa largura de banda e o bot acrescenta informação proveniente de serviços externos.

---

# 🌦️ Fontes de informação portuguesas

## IPMA

A antiga integração com AEMET/serviços espanhóis é substituída por **IPMA**.

O adaptador encontra-se em:

```text
sources/ipma_pt.py
```

É utilizado para:

- previsão meteorológica;
- observações meteorológicas;
- avisos meteorológicos;
- sismicidade;
- risco de incêndio.

A API pública do IPMA disponibiliza estes conjuntos de dados através de endpoints públicos.

O objetivo é que o bot possa responder a pedidos como:

```text
/clima
```

ou utilizar a informação meteorológica nos serviços automáticos sem depender de AEMET.

---

# 🌎 Sismos

A fonte de sismos passa de:

```text
EMSC
```

para:

```text
IPMA
```

O adaptador encontra-se em:

```text
sources/ipma_pt.py
```

São mantidos mecanismos de:

- deduplicação;
- limiar mínimo de magnitude;
- notificação;
- envio para Meshtastic;
- notificação Telegram.

A intenção é evitar que pequenos eventos gerem tráfego desnecessário na mesh.

---

# 🔥 Incêndios

A lógica espanhola:

```text
INFOCA
NASA FIRMS
```

é retirada.

A arquitetura portuguesa passa a considerar:

```text
IPMA
  │
  ├── risco de incêndio
  │
SGIFR / ICNF
  │
  └── ocorrências

ANEPC
  │
  └── avisos à população
```

O adaptador inicial está em:

```text
sources/sgifr_pt.py
```

### Importante

A primeira implementação é deliberadamente conservadora.

Não são inventadas coordenadas de incêndios quando a fonte pública não fornece uma estrutura suficientemente estável.

A próxima evolução deverá utilizar uma camada estruturada de dados públicos, por exemplo ESRI/GeoJSON/CSV quando disponível, permitindo:

```text
🔥 Incêndio
📍 coordenadas
📌 concelho
🚒 meios
👨‍🚒 operacionais
📊 estado
```

e, posteriormente, enviar um **waypoint Meshtastic**.

---

# 🏔️ Integração SOTA

A funcionalidade SOTA é mantida, mas adaptada para Portugal.

O parser passa a reconhecer referências:

```text
CT/AL-001
CT/BA-012
CT/TM-005
```

e rejeita referências que não pertençam à associação `CT` suportada nesta primeira fase.

O adaptador encontra-se em:

```text
sources/sota_pt.py
```

A intenção é permitir uma integração deste tipo:

```text
Meshtastic
     │
     │ /sota CT/AL-001 7.118 SSB
     ▼
    Bot
     │
     ▼
 SOTAwatch
```

e posteriormente também o fluxo inverso:

```text
SOTAwatch
     │
     ▼
 Bot
     │
     ▼
Meshtastic
```

permitindo consultar spots SOTA através da mesh.

> A API de SOTA deve ser validada contra a infraestrutura atual antes de ativar publicação automática em produção.

---

# 📡 Routers fixos

Uma diferença importante em relação ao projeto original é a remoção da dependência de uma lista como:

```python
ROUTERS_VIGILADOS = {
    ...
}
```

O fork português **não pressupõe que determinados nós são routers oficiais**.

A rede pode crescer e mudar sem ser necessário alterar o código do bot.

Em vez de:

```text
Router AL01
Router AL02
Router SE01
...
```

o bot trabalha com:

```text
nós conhecidos
nós ouvidos recentemente
tráfego
ocupação
informação disponível na interface Meshtastic
```

Isto torna o sistema muito mais adequado para uma rede comunitária distribuída.

---

# 🛰️ Possível utilização na Meshtastic Portugal

Uma aplicação particularmente interessante é utilizar o bot como ponte entre a mesh e serviços externos.

Por exemplo:

```text
                 INTERNET
                     │
        ┌────────────┴────────────┐
        │                         │
     SOTAwatch                  IPMA
        │                         │
        └────────────┬────────────┘
                     │
                 BOT PT
                     │
                  MQTT
                     │
              Meshtastic mesh
                     │
          ┌──────────┼──────────┐
          │          │          │
        Algarve   Beira      Minho
```

Um operador numa montanha pode, por exemplo, publicar um spot SOTA através da mesh sem necessitar de dados móveis no próprio rádio/telefone.

---

# 🧩 Estrutura do projeto

```text
bot-meshtastic-pt/
│
├── bot_meshtastic.py
├── potato_fusion.py
│
├── config/
│   └── regions_ct.py
│
├── sources/
│   ├── ipma_pt.py
│   ├── sgifr_pt.py
│   └── sota_pt.py
│
├── tests/
│   └── test_regions.py
│
├── .env.example
├── requirements.txt
└── README.md
```

### `config/regions_ct.py`

Define as regiões SOTA portuguesas.

### `sources/ipma_pt.py`

Integração com IPMA.

### `sources/sgifr_pt.py`

Camada portuguesa para incêndios/ocorrências.

### `sources/sota_pt.py`

Parser e integração SOTA para `CT`.

### `tests/`

Testes unitários das regiões e referências SOTA.

---

# ⚙️ Instalação

## Requisitos

Recomendado:

```text
Python 3.11+
Linux
Meshtastic Python
SQLite
MQTT opcional
Telegram opcional
```

Instalar dependências:

```bash
pip install -r requirements.txt
```

Criar configuração:

```bash
cp .env.example .env
```

Editar:

```bash
nano .env
```

e preencher as credenciais necessárias.

---

# 🧪 Testes

Executar:

```bash
python3 -m pytest -q
```

Os testes atuais verificam principalmente:

- existência das 11 regiões CT;
- nomes das regiões;
- parsing de referências SOTA;
- formatos `CT/XX-nnn`;
- formatos `CT-XX-nnn`;
- formatos `XX-nnn`.

---

# 🔐 Configuração

As credenciais nunca devem ser colocadas diretamente no código.

Utilizar `.env` para:

```text
TELEGRAM_TOKEN
MQTT_*
SOTA_USER
SOTA_PASS
OPENAI_API_KEY
QRZ_*
HAMQTH_*
```

O `.env` deve permanecer fora do Git.

---

# 🛣️ Roadmap

## Fase 1 — 🇵🇹 Base portuguesa

- [x] Estrutura do fork
- [x] Regiões SOTA CT
- [x] Parser SOTA português
- [x] Remoção de routers fixos
- [x] Remoção da gasolina
- [x] Adaptador IPMA
- [x] Adaptador inicial SGIFR
- [ ] Validação integral da execução do bot original
- [ ] Atualização completa do `.env.example`

## Fase 2 — 🏔️ SOTA

- [ ] Validar API atual
- [ ] Publicação de spots
- [ ] Consulta de spots
- [ ] Cache de spots
- [ ] Deduplicação
- [ ] Filtro por região CT
- [ ] Comandos Meshtastic `/sota`

## Fase 3 — 🔥 Incêndios

- [ ] Fonte estruturada ANEPC/ICNF
- [ ] Coordenadas
- [ ] Waypoints Meshtastic
- [ ] Geofencing por região
- [ ] Deduplicação
- [ ] Alertas apenas quando relevantes

## Fase 4 — 🌦️ Meteorologia

- [ ] Comandos IPMA
- [ ] Previsão por região SOTA
- [ ] Avisos por proximidade
- [ ] Meteorologia de cume
- [ ] Integração com posição Meshtastic

## Fase 5 — 🇵🇹 Portugal completo

- [ ] CT continental
- [ ] CT3 Madeira
- [ ] CU Açores

---

# 🤝 Relação com o projeto original

Este projeto é uma **adaptação/fork** do trabalho de:

**nandoraya — [bot-ea7](https://github.com/nandoraya/bot-ea7)**

O objetivo não é substituir ou desvalorizar o projeto original.

A ideia é manter o trabalho técnico desenvolvido no `bot-ea7` e criar uma variante orientada para:

- Portugal;
- comunidade Meshtastic Portugal;
- regiões SOTA portuguesas;
- fontes de informação portuguesas;
- infraestrutura Meshtastic distribuída.

Alterações específicas do fork português devem permanecer identificáveis no histórico Git.

---

# 📜 Licença

Consultar a licença e os termos do projeto original antes de redistribuir ou publicar uma versão derivada.

Este fork deve manter os avisos de copyright e licença exigidos pelo projeto original.

---

# 🇵🇹 Meshtastic Portugal

Este projeto pretende ser uma ferramenta para a comunidade Meshtastic em Portugal.

A filosofia é simples:

> **usar a mesh quando não existe Internet, e usar a Internet apenas onde ela é necessária para trazer informação útil de volta para a mesh.**

Meshtastic transporta a informação.  
O bot faz a integração.  
IPMA, SOTA, SGIFR e outras fontes fornecem os dados.

**Mesh → Gateway → Serviço → Mesh**
