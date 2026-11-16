# Dashboard de zoonoses

Integração local: **SQLite tratado → exportador Python → JSON → dashboard**.
Não depende de planilhas ou bibliotecas Python externas. Use Python 3.10 ou superior.

## Abrir e atualizar

No Windows, dê dois cliques em **Abrir Dashboard.bat**. Ele atualiza os dados e
abre o navegador automaticamente. Mantenha a janela que aparece aberta enquanto
usa o painel; feche-a para encerrar. Se a porta 8000 estiver ocupada, o iniciador
escolhe outra porta livre. Execute novamente o atalho quando o banco for atualizado.

Como alternativa, pelo terminal:

Na pasta do projeto, execute:

```powershell
python exportar_dashboard.py
python -m http.server 8000 --bind 127.0.0.1
```

Abra http://localhost:8000/dashboard_atualizado.html. Para encerrar o servidor, pressione Ctrl+C.
Abrir o HTML com duplo clique não carrega o JSON: use o endereço local acima.

Depois que o tratamento atualizar o banco, execute novamente `python exportar_dashboard.py`
e recarregue a página. O painel mostra a data da exportação, não uma sincronização em tempo real.

Para usar outro banco ou destino:

```powershell
python exportar_dashboard.py --banco "caminho/banco_zoonoses.db" --saida "dados/dashboard.json"
```

O exportador abre o banco somente para leitura. Não executa o gerador, o tratamento
nem as células de recuperação dos notebooks e não altera os dados existentes.

## Regras dos indicadores

- Animais vêm de `animais`. IDs de texto são preservados para vincular os eventos.
- `Cachorro` aparece como `Cão`; situação `Em dia` aparece como `Completa`,
  `Parcial` continua parcial e `Pendente` aparece como `Incompleta`.
- “Vacinação em dia” representa a situação cadastrada do animal; não é uma
  cobertura epidemiológica calculada a partir das doses.
- Só vacinações com situação `Aplicada` entram em doses, com uma dose por registro.
- Município e espécie das vacinações e município dos diagnósticos vêm do animal vinculado.
- Diagnósticos mostram sua situação. Evolução separada não existe no banco.
- Maus-tratos mostram tipo e situação. Gravidade não existe no banco.
- Registros sem data válida continuam nos totais sem filtro de período, mas não
  aparecem em séries mensais e ficam fora de seleções por ano/mês.
- A data de cadastro vem da tabela tratada. O tratamento atual a define no momento
  do processamento; o painel não a interpreta como a data de acolhimento.
- Idade, castrações, adoções e notificações por bairro não são inferidas. Canil e
  notificações aguardam uma próxima adaptação; suas estruturas foram preservadas.

Os dados fornecidos são sintéticos, para fins acadêmicos.

## GitHub

Repositório: https://github.com/LucasEsrom/Painel-de-Zoonoses-e-Controle-Animal

Em **Settings → Pages → Build and deployment → Source**, selecione **GitHub Actions**.
Depois execute **Actions → Publicar dashboard → Run workflow** se a publicação não
tiver iniciado automaticamente.

O workflow `.github/workflows/preparar-dashboard.yml` testa o exportador, valida o
JSON e publica a página quando o JSON ou o código são enviados à branch `main`.
O site recebe somente `index.html` e `dados/dashboard.json`; o banco não entra nos
arquivos servidos pelo Pages nem no repositório. O SQLite é mantido localmente.

Endereço esperado após uma publicação bem-sucedida:
https://lucasesrom.github.io/Painel-de-Zoonoses-e-Controle-Animal/

Para atualizar, execute `python exportar_dashboard.py` no computador que possui
o banco tratado e envie somente `dados/dashboard.json` à branch `main`.
GitHub não acompanha automaticamente as alterações feitas no Google Drive: o JSON
atualizado precisa chegar ao repositório para este fluxo funcionar.

Para executar a versão baixada do GitHub localmente, use `python -m http.server 8000`
e abra o HTML pelo endereço local. O iniciador com dois cliques e o exportador precisam
do arquivo `banco_zoonoses.db` na pasta; esse arquivo não é distribuído no repositório.

Os notebooks originais continuam configurados para Colab/Drive e foram preservados.
Converter a geração e o tratamento para execução automática é uma etapa separada.

## Verificar

```powershell
python -m unittest discover -s tests -v
```
