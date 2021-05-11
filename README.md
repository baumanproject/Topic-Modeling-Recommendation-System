# Topic-Modeling-Recommendation-System
Backend for topic modeling recommendation  system
### Get model
from [source](https://drive.google.com/drive/folders/1SAT_1nRWMo2DOnGWe3oDBiZAwXevGx7f?usp=sharing):

1. Download file dataset.vw  and substitute the same one  in /opt/vw/prod/ folder
2. Download folder batches and copy it's data to /opt/prod/dataset_batch
3. Download folder model_sources and copy it's data to /opt/tm_model/tm_model_sources

### Run project
2. if needed - run docker-compose up in /Postgres directory to run PostgreSql docker container
3. in /scripts folder run :
  + sync.sh
  + inf.sh
4. for retrain run rt.sh in /scripts


