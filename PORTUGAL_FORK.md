
# bot-meshtastic-pt

Base: `nandoraya/bot-ea7`.

## Remover
- routers fixos;
- AEMET;
- EMSC;
- INFOCA;
- NASA FIRMS;
- gasolina.

## Substituir
- províncias espanholas -> 11 regiões SOTA CT;
- meteorologia/avisos/sismos/risco de incêndio -> IPMA;
- incêndios/avisos operacionais -> SGIFR/ICNF/ANEPC;
- referências SOTA -> CT/XX-nnn.

## Regiões CT
AA Alto Alentejo
AL Algarve
BA Beira Alta
BB Beira Baixa
BL Beira Litoral
BT Baixo Alentejo
DL Douro Litoral
ES Estremadura
MN Minho
RB Ribatejo
TM Trás-os-Montes e Alto Douro

## Aplicação
```bash
git clone <o-teu-fork>
cd <o-teu-fork>
cp -a /caminho/bot-meshtastic-pt-fork-kit/{config,sources,tests,patch_portugal.py} .
python3 patch_portugal.py
python3 -m pytest -q
git diff
```

O script cria `bot_meshtastic.py.pre-portugal` antes de alterar o ficheiro.

## Nota
A camada SGIFR inicial é deliberadamente conservadora: usa a página pública para
sinalizar ocorrências, mas não inventa coordenadas. A ligação a uma camada
estruturada ANEPC/ICNF (ESRI/CSV) deve ser a próxima iteração se quisermos
waypoints de incêndio.

O IPMA disponibiliza oficialmente avisos, sismicidade, previsão diária e risco
de incêndio na sua API. O SGIFR/ICNF disponibiliza informação pública de
ocorrências e o ANEPC mantém os Avisos à População.
