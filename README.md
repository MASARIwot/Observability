
### Starting:
```sh
python -m venv .venv
source .venv\\Scripts\\activate
pip install -e .
# run script or flask run and flask run -p 5001 
run-tracer
# in the separate terminal
run-tracer 5001
```


## Setup Jaeger 
```sh
docker run -d --name jaeger \
    -e COLLECTOR_ZIPKIN_HTTP_PORT=9411 \
    -e METRICS_BACKEND=prometheus \
    -p 5775:5775/udp \
    -p 6831:6831/udp \
    -p 6832:6832/udp \
    -p 5778:5778 \
    -p 16686:16686 \
    -p 14268:14268 \
    -p 14250:14250 \
    -p 9411:9411 \
    jaegertracing/all-in-one:1.29
```
### Jaeger UI
http://localhost:16686/search

`METRICS_BACKEND=prometheus` is an environment variable that configures Jaeger to expose metrics in Prometheus format.<br>
With the above configuration, Jaeger will expose its metrics at the `/metrics` endpoint on port `14269` by default.<br>
If you're using a custom configuration, make sure the metrics endpoint is enabled and exposed.
`-e METRICS_HTTP_PORT=14269`


## Setup Prometheus to Scrape Jaeger's Metrics

```sh
docker run \
    -d \
    --name prometheus \
    -p 9090:9090 \
    -v .//prometheus.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus

```

Configure Prometheus to scrape the metrics from the Jaeger instance <br>
we need to add scrape job to your prometheus.yml configuration file:
```yaml
scrape_configs:
  - job_name: 'jaeger'
    static_configs:
      - targets: ['localhost:14269']  # Adjust the host and port as necessary

```



###  Note:
## Persistent storage
Prometheus stores its data in the `/prometheus` directory inside the container. <br>
As a result, this data is lost every time the container is restarted. <br>
To ensure your data is preserved, you should set up persistent storage or use bind mounts for your container.
### Create persistent volume for your data
```sh
docker volume create prometheus-data
```
### Start Prometheus container
```sh
docker run \
    -p 9090:9090 \
    -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
    -v prometheus-data:/prometheus \
    prom/prometheus
```

## Steps metric data rotation in Prometheus

### Configure Data Retention
Prometheus allows you to set how long it should retain metric data before it is automatically deleted. <br> You can configure this using the `--storage.tsdb.retention.time` flag when starting Prometheus.

```sh
docker run -d \
    --name prometheus \
    -p 9090:9090 \
    -v prometheus_data:/prometheus \
    prom/prometheus \
    --storage.tsdb.retention.time=30d
```
`--storage.tsdb.retention.time=30d` : This flag tells Prometheus to retain metric data for 30 days. <br>  After 30 days, older data will be automatically deleted. <br> 
You can also set the retention time in hours (h), minutes (m), or even seconds (s), depending on your needs.

### Control Storage Size

Instead of setting a time-based retention policy, you can limit the size of the data stored by Prometheus<br>  using the `--storage.tsdb.retention.size` flag. <br>
For example:
```sh
docker run -d \
    --name prometheus \
    -p 9090:9090 \
    -v prometheus_data:/prometheus \
    prom/prometheus \
    --storage.tsdb.retention.size=50GB

```

### All together
`docker-compose.yml`
```yaml 
version: '3'
services:
  jaeger:
    image: jaegertracing/all-in-one:1.29
    container_name: jaeger
    environment:
      - COLLECTOR_ZIPKIN_HTTP_PORT=9411
      - METRICS_BACKEND=prometheus
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"

  prometheus:
    image: prom/prometheus
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - prometheus_data:/prometheus
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - "--storage.tsdb.retention.time=30d"
      - "--storage.tsdb.retention.size=50GB"

volumes:
  prometheus_data:

```
Logs
```sh
docker volume create prometheus_data
docker-compose up -d
docker-compose logs jaeger
docker-compose logs prometheus
```

```
docker ps -a --filter "name=prometheus"
docker rm prometheus

```