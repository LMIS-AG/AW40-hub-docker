#!/bin/bash

set -e

mongosh <<EOF
use admin
db.createUser({
  user:  '$MONGO_INITDB_API_USERNAME',
  pwd: '$MONGO_INITDB_API_PASSWORD',
  roles: [
    {role: 'readWrite', db: '$MONGO_INITDB_DB'},
    {role: 'readWrite', db: '$MONGO_INITDB_DB-test'}
  ]
})
EOF