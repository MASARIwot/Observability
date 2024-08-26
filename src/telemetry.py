from flask import request
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from requests import PreparedRequest
import uuid
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


def configure_opentelemetry(app):
    # Set the global propagator to TraceContextTextMapPropagator

    def _flask_request_hook(span, flask_request_environ):
        if not request.url_rule:
            return
        span.update_name(request.endpoint or request.url_rule.rule)
        span.set_attribute(
            "correlation", str(uuid.uuid4())
        )  # Get correlation from global of from request header

    def _requests_hook(span: Span, request: PreparedRequest):
        span.update_name('requests:' + request.method + ":" + request.path_url.split("?")[0])
        span.set_attribute("correlation", str(uuid.uuid4())) # Get correlation from global of from request header

    set_global_textmap(TraceContextTextMapPropagator())

    # OpenTelemetry Configuration
    trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "tracer"})))
    tracer = trace.get_tracer(__name__)

    # Configure OpenTelemetry to export traces to an OTLP collector
    main_exporter = OTLPSpanExporter(
        agent_host_name="localhost",  # Replace with your Jaeger host
        agent_port=4317,  # Default Jaeger port
    )
    batch_span_processor = BatchSpanProcessor(main_exporter)
    trace.get_tracer_provider().add_span_processor(batch_span_processor)

    # Add a SimpleSpanProcessor with a ConsoleSpanExporter to log spans to the console
    console_exporter = ConsoleSpanExporter()
    simple_span_processor = SimpleSpanProcessor(console_exporter)
    trace.get_tracer_provider().add_span_processor(simple_span_processor)

    # Automatically instrument the Flask app
    FlaskInstrumentor().instrument_app(
        app, excluded_urls="/api-spec,/doc", request_hook=_flask_request_hook
    )

    # Automatically instrument the requests library, will add Traceparent to all request
    RequestsInstrumentor().instrument(request_hook=_requests_hook)

