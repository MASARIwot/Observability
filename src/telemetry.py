from flask import request
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    ConsoleSpanExporter,

)
from opentelemetry.sdk.resources import (
    SERVICE_NAME,
    Resource,
    SERVICE_NAMESPACE,
    SERVICE_INSTANCE_ID,
)

# from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from requests import PreparedRequest
import uuid
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader

import socket
from opentelemetry.trace import Status, StatusCode


# if platform.system() == "Windows":
#     # Implement Windows-specific logic here, for example:
#     num_handles = proc.num_handles()  # Windows has a `num_handles()` method
#     print(f"Number of handles: {num_handles}")
# else:
#     num_fds = proc.num_fds()
#     print(f"Number of file descriptors: {num_fds}")

def initialize_metrics():

    # Customize the system metrics initialization here
    # if os.name == 'nt': 
    #     proc = psutil.Process()
    #     print("Disable open file descriptors on Windows")
    #     proc.num_fds = proc.num_handles

    SystemMetricsInstrumentor().instrument()



def configure_opentelemetry(app):
    # Set the global propagator to TraceContextTextMapPropagator

    def _flask_request_hook(span, flask_request_environ):
        if not request.url_rule:
            return
        span.update_name(request.endpoint or request.url_rule.rule)
        span.set_attribute(
            "correlation", str(uuid.uuid4())
        )  # Get correlation from global of from request hea

    def _flask_response_hook(span: Span, status, response_headers):
        print(type(status))
        if "200" in status:
            span.set_status(StatusCode.OK)
        else:
            span.set_status(Status(StatusCode.ERROR))

        print(status)
        print(response_headers)
        # span.set_status(Status(StatusCode.ERROR))
        # span.set_status(StatusCode.OK)
        print(span.status)
        print(span.status.status_code)
        # We need it globally
        # record_exception

    def _requests_hook(span: Span, request: PreparedRequest):
        span.update_name(
            "requests:" + request.method + ":" + request.path_url.split("?")[0]
        )
        span.set_attribute(
            "correlation", str(uuid.uuid4())
        )  # Get correlation from global of from request header

    set_global_textmap(TraceContextTextMapPropagator())

    resource = Resource.create(
        {
            SERVICE_NAME: "tracer",
            SERVICE_NAMESPACE: "observation",
            SERVICE_INSTANCE_ID: socket.gethostname(),
        }
    )
    # OpenTelemetry Configuration
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)

    # Configure OpenTelemetry to export traces to an OTLP collector
    main_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    batch_span_processor = BatchSpanProcessor(main_exporter)
    trace.get_tracer_provider().add_span_processor(batch_span_processor)

    # Configure OpenTelemetry periodic metrics exporter
    console_metric_exporter = ConsoleMetricExporter()
    console_metric_reader = PeriodicExportingMetricReader(console_metric_exporter, export_interval_millis=30000)
    # metrics_exporter = OTLPMetricExporter(endpoint="http://localhost:4317/v1/metrics", insecure=True)
    metrics_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
    metric_reader = PeriodicExportingMetricReader(exporter=metrics_exporter, export_interval_millis=30000)
    meter_provider=MeterProvider(resource=resource, metric_readers=[metric_reader, console_metric_reader])
    metrics.set_meter_provider(meter_provider)
    

    # Add a SimpleSpanProcessor with a ConsoleSpanExporter to log spans to the console
    console_exporter = ConsoleSpanExporter()
    simple_span_processor = SimpleSpanProcessor(console_exporter)
    trace.get_tracer_provider().add_span_processor(simple_span_processor)
    # calls_total{service_name="tracer", span_name="sample.api-propagate"}
    
    # SystemMetricsInstrumentor().instrument()
    # Then, use this function instead of the default initialization
    initialize_metrics()
    
    
    # Automatically instrument the Flask app
    FlaskInstrumentor().instrument_app(
        app,
        excluded_urls="/api-spec,/doc",
        request_hook=_flask_request_hook,
        response_hook=_flask_response_hook,
    )

    # Automatically instrument the requests library, will add Traceparent to all request
    RequestsInstrumentor().instrument(request_hook=_requests_hook)
    URLLib3Instrumentor().instrument()


#  TODO
#     # Create a meter
#     meter = metrics.get_meter(__name__)

#     # Example: Create and record a counter metric. or dome other
#     request_counter = meter.create_counter(
#         name="http_requests_total",
#         description="Total number of HTTP requests",
#         unit="1",
#     )

#     # Function to record metrics
#     def record_request_metrics():
#         request_counter.add(1, {"service.name": "tracer"})


