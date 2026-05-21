// Aguarda o MongoDB estar pronto e inicializa o Replica Set
rs.initiate({
  _id: "ualspped-rs", //"rs0"
  members: [
    { _id: 0, host: "mongo-primary:27017", priority: 2 },
    { _id: 1, host: "mongo-secondary1:27017", priority: 1 },
    { _id: 2, host: "mongo-secondary2:27017", priority: 1 }
  ]
});

print(" Replica Set iniciado com sucesso!");