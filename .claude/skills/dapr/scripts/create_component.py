#!/usr/bin/env python3
"""
Generate Dapr component YAML files from templates.
Usage: python create_component.py <component-type> <name> [options]
"""

import argparse
import sys
from pathlib import Path

COMPONENT_TEMPLATES = {
    "state.redis": """apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: {name}
  namespace: {namespace}
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: {redis_host}
  - name: redisPassword
    value: {redis_password}
  - name: enableTLS
    value: "{enable_tls}"
scopes:
{scopes}
""",
    "pubsub.redis": """apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: {name}
  namespace: {namespace}
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: {redis_host}
  - name: redisPassword
    value: {redis_password}
  - name: enableTLS
    value: "{enable_tls}"
scopes:
{scopes}
""",
    "bindings.kafka": """apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: {name}
  namespace: {namespace}
spec:
  type: bindings.kafka
  version: v1
  metadata:
  - name: brokers
    value: {brokers}
  - name: topics
    value: {topics}
  - name: consumerGroup
    value: {consumer_group}
  - name: authType
    value: {auth_type}
scopes:
{scopes}
""",
    "secretstores.kubernetes": """apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: {name}
  namespace: {namespace}
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
""",
}


def format_scopes(scopes_list):
    """Format scopes list into YAML format."""
    if not scopes_list:
        return "  - '*'"
    return "\n".join(f"  - {scope}" for scope in scopes_list)


def generate_component(component_type, name, **kwargs):
    """Generate component YAML from template."""
    if component_type not in COMPONENT_TEMPLATES:
        print(f"❌ Unknown component type: {component_type}")
        print(f"Available types: {', '.join(COMPONENT_TEMPLATES.keys())}")
        sys.exit(1)

    template = COMPONENT_TEMPLATES[component_type]

    # Default values
    defaults = {
        "namespace": "default",
        "redis_host": "localhost:6379",
        "redis_password": "",
        "enable_tls": "false",
        "brokers": "localhost:9092",
        "topics": "topic1",
        "consumer_group": "group1",
        "auth_type": "none",
        "scopes": "  - '*'",
    }

    # Override with provided kwargs
    params = {**defaults, **kwargs, "name": name}

    # Format scopes if provided as list
    if "scopes_list" in kwargs:
        params["scopes"] = format_scopes(kwargs["scopes_list"])

    return template.format(**params)


def main():
    parser = argparse.ArgumentParser(description="Generate Dapr component YAML files")
    parser.add_argument("type", help="Component type (e.g., state.redis, pubsub.redis)")
    parser.add_argument("name", help="Component name")
    parser.add_argument("--namespace", default="default", help="Kubernetes namespace")
    parser.add_argument("--redis-host", help="Redis host:port")
    parser.add_argument("--redis-password", default="", help="Redis password")
    parser.add_argument("--enable-tls", action="store_true", help="Enable TLS")
    parser.add_argument("--brokers", help="Kafka brokers (comma-separated)")
    parser.add_argument("--topics", help="Kafka topics (comma-separated)")
    parser.add_argument("--consumer-group", help="Kafka consumer group")
    parser.add_argument("--scopes", help="App scopes (comma-separated)")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    # Prepare kwargs
    kwargs = {
        "namespace": args.namespace,
        "enable_tls": str(args.enable_tls).lower(),
    }

    if args.redis_host:
        kwargs["redis_host"] = args.redis_host
    if args.redis_password:
        kwargs["redis_password"] = args.redis_password
    if args.brokers:
        kwargs["brokers"] = args.brokers
    if args.topics:
        kwargs["topics"] = args.topics
    if args.consumer_group:
        kwargs["consumer_group"] = args.consumer_group
    if args.scopes:
        kwargs["scopes_list"] = [s.strip() for s in args.scopes.split(",")]

    # Generate component
    yaml_content = generate_component(args.type, args.name, **kwargs)

    # Output
    if args.output:
        Path(args.output).write_text(yaml_content)
        print(f"✅ Component created: {args.output}")
    else:
        print(yaml_content)


if __name__ == "__main__":
    main()
