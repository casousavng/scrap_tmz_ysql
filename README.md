# Projeto: Extração de Notícias do TMZ.com

## Descrição
Este projeto consiste num script Python que extrai dados de notícias do site [TMZ.com](https://www.tmz.com), com base numa lista de nomes de pesquisa fornecida num ficheiro JSON. As notícias extraídas são armazenadas numa base de dados MySQL hospedada na cloud através do serviço [Aiven.io](https://aiven.io/).

### Funcionalidades
- Pesquisa automatizada de notícias no TMZ.com com base numa lista de celebridades/termos de interesse.
- Extração de dados como título, conteúdo, datas de criação/publicação/modificação, e link da notícia.
- Armazenamento organizado em tabelas na base de dados MySQL (uma tabela por termo de pesquisa).
- Atualização de dados de notícias já existentes (caso haja modificações no conteúdo).

---

## Requisitos
Para executar este projeto, são necessárias as seguintes ferramentas e bibliotecas:

### Dependências:
- Python 3.8 ou superior
- [MySQL](https://www.mysql.com/)

### Bibliotecas Python:
Instale as bibliotecas necessárias com os seguintes comandos:
```bash
pip install mysql-connector-python
pip install requests
pip install beautifulsoup4
```

### Configuração do Ambiente:
1. Crie uma conta em [Aiven.io](https://console.aiven.io/) para hospedar a base de dados MySQL.
2. Configure as credenciais da base de dados no código:
   - `user`
   - `password`
   - `host`
   - `port`

Certifique-se de que a base de dados está online e as credenciais estão corretas antes de executar o script.

---

## Estrutura do Projeto
O projeto é composto pelos seguintes ficheiros principais:
- **`script.py`**: O script Python principal.
- **`nomes.json`**: Ficheiro JSON contendo os termos/nomes a serem pesquisados.

### Estrutura do Ficheiro JSON (`nomes.json`):
```json
{
  "tipo1": ["Nome1", "Nome2"],
  "tipo2": ["Nome3", "Nome4"]
}
```
Cada "tipo" corresponde a uma categoria de termos de pesquisa.

---

## Como Executar
1. Certifique-se de que todas as dependências estão instaladas.
2. Configure a base de dados no serviço Aiven.io e atualize as credenciais no script.
3. Insira os nomes de pesquisa no ficheiro `nomes.json`.
4. Execute o script:
   ```bash
   python script.py
   ```
5. O progresso será exibido no terminal, e os dados serão armazenados na base de dados.

---

## Notas Importantes
- Certifique-se de que o servidor MySQL está online antes de iniciar o script.
- Evite consultas em excesso ao TMZ.com para prevenir bloqueios por parte do site.
- Dados são organizados em tabelas individuais com base no termo de pesquisa, substituindo espaços por `_` (underscore).

---

## Melhorias Futuras
- Implementar suporte para múltiplas fontes de notícias.
- Adicionar suporte para gráficos ou relatórios automáticos baseados nos dados recolhidos.
- Expandir para suportar bases de dados alternativas, como PostgreSQL.

---

# Project: TMZ.com News Scraper

## Description
This project consists of a Python script that extracts news data from the [TMZ.com](https://www.tmz.com) website based on a list of search terms provided in a JSON file. The extracted news is stored in a MySQL database hosted in the cloud using the [Aiven.io](https://aiven.io/) service.

### Features
- Automated search for news on TMZ.com based on a list of celebrities/terms of interest.
- Extraction of data such as title, content, creation/publication/modification dates, and news link.
- Organized storage in MySQL database tables (one table per search term).
- Update of news data if changes are detected in existing entries.

---

## Requirements
To run this project, the following tools and libraries are required:

### Dependencies:
- Python 3.8 or higher
- [MySQL](https://www.mysql.com/)

### Python Libraries:
Install the required libraries with the following commands:
```bash
pip install mysql-connector-python
pip install requests
pip install beautifulsoup4
```

### Environment Setup:
1. Create an account on [Aiven.io](https://console.aiven.io/) to host the MySQL database.
2. Configure the database credentials in the code:
   - `user`
   - `password`
   - `host`
   - `port`

Ensure that the database is online and credentials are correct before running the script.

---

## Project Structure
The project consists of the following main files:
- **`script.py`**: The main Python script.
- **`nomes.json`**: JSON file containing the search terms/names.

### JSON File Structure (`nomes.json`):
```json
{
  "type1": ["Name1", "Name2"],
  "type2": ["Name3", "Name4"]
}
```
Each "type" corresponds to a category of search terms.

---

## How to Run
1. Ensure all dependencies are installed.
2. Configure the database on Aiven.io and update the credentials in the script.
3. Add the search terms to the `nomes.json` file.
4. Run the script:
   ```bash
   python script.py
   ```
5. Progress will be displayed in the terminal, and the data will be stored in the database.

---

## Important Notes
- Make sure the MySQL server is online before starting the script.
- Avoid excessive queries to TMZ.com to prevent being blocked by the website.
- Data is organized into individual tables based on the search term, replacing spaces with `_` (underscore).

---

## Future Improvements
- Implement support for multiple news sources.
- Add support for automatic reports or graphs based on the collected data.
- Expand to support alternative databases like PostgreSQL.
