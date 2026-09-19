# 🏎️ UALSpeed — Sistema Distribuído de Gestão de Dados de Fórmula 1

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![MongoDB](https://img.shields.io/badge/MongoDB-7-darkgreen)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Docker](https://img.shields.io/badge/Docker-Swarm-blue)
![Nginx](https://img.shields.io/badge/Nginx-1.31-brightgreen)

Sistema distribuído de gestão de resultados de Fórmula 1, implementado
com microserviços, replicação de dados, cluster Docker Swarm e
interface web em tempo real.

---

## 📋 Índice

- [Arquitectura do Sistema](#arquitectura-do-sistema)
- [Funcionalidades Implementadas](#funcionalidades-implementadas)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Projecto](#estrutura-do-projecto)
- [Como Executar](#como-executar)
- [Testes do Sistema](#testes-do-sistema)
- [Interface Web](#interface-web)
- [Docker Swarm](#docker-swarm)
- [Autor](#autor)

---

## 🏗️ Arquitectura do Sistema

<img width="402" height="330" alt="Captura de ecrã 2026-09-19 181244" src="https://github.com/user-attachments/assets/fce74438-ecba-462d-8bef-e732deaa62dc" />



### Fluxo de dados

Carro F1 → data-processor → Redis (Pub/Sub) → results-manager → MongoDB
↓
Replica Set
(Primary + 2 Secondary)

---

## ✅ Funcionalidades Implementadas

### Funcionalidade 1 — Tecnologias de Sistemas Distribuídos
- Dois serviços independentes que comunicam entre si
- `data-processor` — recebe e valida dados de telemetria via REST API
- `results-manager` — processa classificações e resultados
- Fila de mensagens **Redis Pub/Sub** para comunicação assíncrona
- Paralelismo de Pipeline — processamento em estágios independentes

### Funcionalidade 2 — Cluster de Computadores (Docker Swarm)
- Cluster configurado com Docker Swarm
- 8 serviços distribuídos pelo cluster
- Escalabilidade dinâmica sem interrupção do serviço
- Adição e remoção de réplicas em tempo real
- Tolerância a falhas com recuperação automática

### Funcionalidade 3 — Virtualização de Computadores
- Container Docker dedicado por cada componente
- `docker-compose.yml` para desenvolvimento local
- `docker-stack.yml` para deploy em cluster Swarm
- Volumes para persistência dos dados de corridas e histórico
- Isolamento completo entre serviços

### Funcionalidade 5 — Estratégias de Replicação de Dados
- **MongoDB Replica Set** com 1 Primary + 2 Secondary
- Replicação assíncrona Master-Slave (estratégia 1)
- **Cache Redis** para dados mais consultados (estratégia 2)
- Eleição automática de novo Primary em caso de falha
- Consistência de dados garantida entre todas as réplicas

### Funcionalidade 6 — Replicação de Serviços
- **Nginx** como load balancer com algoritmo round-robin
- 2 réplicas do `data-processor` em simultâneo
- 2 réplicas do `results-manager` em simultâneo
- Detecção de falhas e redistribuição automática do tráfego
- Sistema resiliente — continua operacional com serviços em falha

### Funcionalidade 7 — Avaliação de Desempenho
- Dashboard web em tempo real (`localhost:8002`)
- Métricas de throughput de eventos processados
- Estado em tempo real de todos os serviços
- Monitorização do cluster Swarm
- Latência e disponibilidade dos serviços

---

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologia | Função |
|---|---|---|
| Serviços | Python 3.11 + FastAPI | APIs REST dos microserviços |
| Base de Dados | MongoDB 7 Replica Set | Persistência e replicação |
| Fila de Mensagens | Redis 7 Pub/Sub | Comunicação entre serviços |
| Load Balancer | Nginx 1.31 | Distribuição de carga |
| Cluster | Docker Swarm | Orquestração de containers |
| Virtualização | Docker + Docker Compose | Containerização |
| Interface Web | HTML + JavaScript | Dashboard e visualização |
| Validação | Pydantic | Validação de dados |
| Driver MongoDB | Motor (async) | Acesso assíncrono ao MongoDB |

---

## 📁 Estrutura do Projecto

UALSpeed/
│
├── services/
│   ├── data-processor/          # Serviço de telemetria
│   │   ├── main.py              # Aplicação FastAPI
│   │   ├── models.py            # Modelos Pydantic
│   │   ├── routes/
│   │   │   └── telemetria.py    # Rotas de telemetria
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── results-manager/         # Serviço de resultados
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py          # Ligação MongoDB
│   │   ├── consumer.py          # Consumer Redis
│   │   ├── routes/
│   │   │   ├── classificacao.py
│   │   │   └── pilotos.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── web-interface/           # Interface web
│       ├── main.py
│       ├── static/
│       │   ├── index.html       # Dashboard de métricas
│       │   ├── corrida.html     # Corrida ao vivo
│       │   └── admin.html       # Painel administrativo
│       ├── requirements.txt
│       └── Dockerfile
│
├── infra/
│   ├── nginx/
│   │   └── nginx.conf           # Configuração do load balancer
│   ├── mongo/
│   │   └── init-replica.js      # Inicialização do Replica Set
│   └── scripts/
│       └── demo-swarm.sh        # Script de demonstração
│
├── docs/
│   └── architecture.md          # Decisões arquitecturais
│
├── docker-compose.yml           # Orquestração local
├── docker-stack.yml             # Deploy Docker Swarm
└── README.md

---

## 🚀 Como Executar

### Pré-requisitos

- Docker Desktop instalado e em execução
- Git

### Desenvolvimento local

```bash
# 1. Clona o repositório
git clone https://github.com/EliandroAgostinho/UALSpeed.git
cd UALSpeed

# 2. Levanta todos os serviços
docker compose up --build

# 3. Inicializa o Replica Set MongoDB
docker exec -it ualspped-mongo-primary mongosh --eval "
rs.initiate({
  _id: 'ualspped-rs',
  members: [
    { _id: 0, host: 'mongo-primary:27017', priority: 2 },
    { _id: 1, host: 'mongo-secondary1:27017', priority: 1 },
    { _id: 2, host: 'mongo-secondary2:27017', priority: 1 }
  ]
})
"

# 4. Acede à interface web
# http://localhost:8002
```

### Docker Swarm (Cluster)

```bash
# 1. Inicializa o Swarm
docker swarm init

# 2. Constrói as imagens
docker compose build

# 3. Faz o deploy no cluster
docker stack deploy -c docker-stack.yml ualspped

# 4. Verifica os serviços
docker service ls

# 5. Inicializa o Replica Set
docker exec -it $(docker ps -q -f name=ualspped_mongo-primary) mongosh --eval "
rs.initiate({
  _id: 'ualspped-rs',
  members: [
    { _id: 0, host: 'mongo-primary:27017', priority: 2 },
    { _id: 1, host: 'mongo-secondary1:27017', priority: 1 },
    { _id: 2, host: 'mongo-secondary2:27017', priority: 1 }
  ]
})
"
```

### Parar o sistema

```bash
# Desenvolvimento local
docker compose down

# Swarm
docker stack rm ualspped
```

---

## 🧪 Testes do Sistema

### Verificar estado dos serviços
```bash
docker compose ps
curl http://localhost/data/health
curl http://localhost/results/health
```

### Verificar Replica Set MongoDB
```bash
docker exec -it ualspped-mongo-primary mongosh \
  --eval "rs.status().members.forEach(m => print(m.name, m.stateStr))"
```

### Testar Load Balancing
```bash
# Hostnames devem alternar entre réplicas
curl http://localhost/data/instancia
curl http://localhost/data/instancia
curl http://localhost/data/instancia
```

### Testar Tolerância a Falhas
```bash
# Para um serviço
docker compose stop data-processor

# Sistema continua operacional
curl http://localhost/results/health

# Recupera
docker compose start data-processor
```

### Testar Eleição MongoDB
```bash
# Para o Primary
docker compose stop mongo-primary

# Secondary é promovido automaticamente
docker exec -it ualspped-mongo-secondary1 mongosh \
  --eval "rs.status().members.forEach(m => print(m.name, m.stateStr))"

# Reinicia o Primary
docker compose start mongo-primary
```

### Testar Escalabilidade no Swarm
```bash
# Escala para 3 réplicas
docker service scale ualspped_data-processor=3

# Escala de volta
docker service scale ualspped_data-processor=2
```

---

## 🌐 Interface Web

| URL | Descrição |
|---|---|
| `http://localhost:8002` | Dashboard de métricas em tempo real |
| `http://localhost:8002/corrida` | Corrida ao vivo com telemetria |
| `http://localhost:8002/admin` | Painel administrativo de pilotos |
| `http://localhost:8000/docs` | API docs do data-processor |
| `http://localhost:8001/docs` | API docs do results-manager |

---

## 🐳 Docker Swarm

### Comandos úteis

```bash
# Lista todos os serviços e réplicas
docker service ls

# Escala um serviço
docker service scale ualspped_data-processor=3

# Logs de um serviço
docker service logs ualspped_results-manager

# Remove o stack
docker stack rm ualspped

# Estado do cluster
docker node ls
```

---

## 👤 Autor

**Eliandro Agostinho**
