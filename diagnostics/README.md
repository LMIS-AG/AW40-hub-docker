# AW40-hub-docker - Diagnostics

A background service that integrates the DFKI State Machine.

## Basic usage
Data (knowledge graph, models, sample signals etc) not yet included in repo.

1. Start the development stack via
```
docker compose --env-file dev.env up -d
```
2. Add Tensorflow models to the [models/](models/) directory. Currently, models
are required to exactly follow the naming convention `<COMPONENT>.h5`.

3. Navigate to http://127.0.0.1:3030 and at a dataset named "/OBD" to the
knowledge graph. Upload example data , e.g. 
[this file](https://github.com/tbohne/obd_ontology/blob/main/knowledge_base/test_kg.ttl)
created by the DFKI.


Now a hypothetical user can interact via the workshop part of the API and start
a diagnosis via a POST request to
`http://127.0.0.1:8000/v1/<WORKSHOP_ID>/cases/<CASE_ID>/diag`.
To get an overview about the current state of the diagnosis and (intermediate)
results visit
`http://127.0.0.1:8000/v1/<WORKSHOP_ID>/cases/<CASE_ID>/diag/report`.
