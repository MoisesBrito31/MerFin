# Projeto Ibovespa - Plataforma de Visualização e Gerenciamento de Ações

---

## Sumário

- [Descrição](#descrição)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Arquitetura](#arquitetura)
- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## Descrição

Este projeto é uma aplicação web para visualização, busca, filtragem e gerenciamento de ações da bolsa brasileira (Ibovespa). Utiliza um backend em Django REST Framework para fornecer APIs RESTful com autenticação por token, incorporando dados financeiros enriquecidos via pandas e yfinance. O frontend é desenvolvido com Vue.js, usando Vue Router para navegação, Vuex para gerenciamento de estado, e BootstrapVue para estilização responsiva e componentes.

---

## Tecnologias Utilizadas

### Frontend

- **Vue.js:** Framework JavaScript progressivo para interfaces reativas.
- **Vue Router:** Gerenciamento e navegação de rotas SPA.
- **Vuex:** Gerenciamento centralizado de estado da aplicação.
- **BootstrapVue:** Componentes Bootstrap adaptados para Vue.
- **Fetch API:** Comunicação com backend via HTTP com controle de autenticação.
- **Componentização:** Organização modular do código em componentes reutilizáveis.

### Backend

- **Django:** Framework web robusto e versátil em Python.
- **Django REST Framework (DRF):** Facilita a criação de APIs RESTful.
- **Pandas:** Biblioteca para tratamento e análise de dados financeiros.
- **yfinance:** Obtém dados financeiros diretamente do Yahoo Finance.
- **Modelos Django:** Representação dos objetos do domínio (Ativo, Setor, Segmento).
- **Serializers DRF:** Transformação dos dados do backend para JSON.
- **Filtros Dinâmicos com Q:** Flexibiliza buscas complexas com filtros condicionais.
- **Token Authentication:** Segurança via autenticação por tokens.

---

## Arquitetura

A aplicação está dividida em duas camadas principais:

- **Backend:** API RESTful em Django, responsável por cuidar da persistência, regras de negócio, autenticação e disponibilização dos dados financeiros.
- **Frontend:** SPA Vue que consome a API fornecendo interface amigável para busca, filtragem, paginação e gestão dos ativos financeiros.

A comunicação se dá via JSON/HTTP com tokens de segurança para assegurar acesso autorizado.

---

## Funcionalidades

- Listagem paginada e ordenável dos ativos do Ibovespa.
- Busca de ativos por código, nome, setor, segmento e tipo.
- Filtros específicos por setor e segmento via selects dinâmicos.
- Adição de ativos à lista personalizada do usuário.
- Autenticação segura via token.
- Feedback visual com carregamento e mensagens de sucesso/erro.
- Navegação fluida usando Vue Router.
- Estado global compartilhado via Vuex (token e domínio do backend).

---

## Instalação

### Backend

1. Clone o repositório:

```bash
git clone <url-do-repositorio>
cd backend
```

2. Crie e ative ambiente virtual (recomendado):

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate   # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute as migrações:

```bash
python manage.py migrate
```

5. Execute o servidor:

```bash
python manage.py runserver
```

### Frontend

1. No diretório `frontend`:

```bash
npm install
npm run serve
```

---

## Configuração

- Configure o backend para ativar autenticação por token.
- No Vuex configure `token` e `dominio` para apontar corretamente para o backend e as credenciais.
- Ajuste `apiUrl` e rotas conforme necessidade.

---

## Como Usar

- Navegue até a página principal.
- Utilize o campo de busca para filtrar ativos por texto.
- Use os selects para filtrar por setor e segmento.
- Clique em "Buscar" para aplicar os filtros.
- Utilize a paginação para navegar entre as páginas.
- Clique no botão "Adicionar" para incluir um ativo à sua lista personalizada.

---

## Estrutura do Projeto

backend/ 

# Backend Django ibovespa/ 
# App Ibovespa, modelos, views, serializers, urls frontend/ 
# Aplicação Vue.js src/ components/ibovespa/ 
# Componentes Vue para ativos e filtros views/ 
# Páginas principais store/ 
# Vuex store para estado global

---

## Contribuição

Sinta-se à vontade para abrir issues e enviar pull requests. Siga as boas práticas e mantenha o padrão do projeto.

---

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

Se desejar mais detalhes, documentação técnica ou ajuda para expandir funcionalidades, estou à disposição!