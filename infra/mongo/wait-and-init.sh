#!/bin/bash
# Espera o mongo-primary estar pronto antes de inicializar o replica set

echo "⏳ Aguardando mongo-primary ficar disponível..."

until mongosh --host mongo-primary:27017 --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
  echo "   MongoDB ainda não está pronto, aguardando 2 segundos..."
  sleep 2
done

echo " mongo-primary disponível!"
echo " Inicializando Replica Set..."

mongosh --host mongo-primary:27017 /init-replica.js

echo " Processo de inicialização concluído!"