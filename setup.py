from setuptools import setup, find_packages

setup(
    name="tracer",
    version="0.1.0",
    description="A Flask application with Flask-Smorest and OpenTelemetry instrumentation",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=2.0.0",
        "flask-smorest",
        "opentelemetry-api",
        "opentelemetry-sdk",
        "opentelemetry-instrumentation-flask",
        "opentelemetry-instrumentation-requests",
        "opentelemetry-exporter-otlp",
        "opentelemetry-exporter-jaeger", # TODO DROP IT
        # "opentelemetry-exporter-prometheus", # TODO
        # "prometheus_client" # TODO
        # "opentelemetry-exporter-otlp-proto-http"
        # "opentelemetry-exporter-otlp-proto-grpc"
    ],
    entry_points={
        "console_scripts": [
            "run-tracer=src.app:main", # or run-tracer 5001
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
