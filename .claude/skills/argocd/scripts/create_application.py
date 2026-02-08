#!/usr/bin/env python3
"""
Generate ArgoCD Application YAML files.
Usage: python create_application.py <name> --repo <url> --path <path> [options]
"""

import argparse
import sys
from pathlib import Path

def generate_application(name, **kwargs):
    """Generate Application YAML."""

    # Base template
    yaml = f"""apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {name}
  namespace: {kwargs.get('namespace', 'argocd')}"""

    # Finalizer
    if kwargs.get('finalizer', True):
        yaml += """
  finalizers:
    - resources-finalizer.argocd.argoproj.io"""

    yaml += f"""
spec:
  project: {kwargs.get('project', 'default')}
  source:
    repoURL: {kwargs['repo_url']}
    targetRevision: {kwargs.get('revision', 'HEAD')}
    path: {kwargs['path']}"""

    # Helm configuration
    if kwargs.get('helm_chart'):
        yaml += f"""
    chart: {kwargs['helm_chart']}"""

    if kwargs.get('helm_values'):
        yaml += """
    helm:
      valueFiles:"""
        for vf in kwargs['helm_values']:
            yaml += f"""
        - {vf}"""

    if kwargs.get('helm_params'):
        if not kwargs.get('helm_values'):
            yaml += """
    helm:"""
        yaml += """
      parameters:"""
        for hp in kwargs['helm_params']:
            yaml += f"""
        - name: {hp['name']}
          value: "{hp['value']}\""""

    # Destination
    yaml += f"""
  destination:
    server: {kwargs.get('dest_server', 'https://kubernetes.default.svc')}
    namespace: {kwargs['dest_namespace']}"""

    # Sync policy
    if kwargs.get('auto_sync'):
        yaml += """
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true"""

        if kwargs.get('prune_last'):
            yaml += """
      - PruneLast=true"""

    return yaml


def main():
    parser = argparse.ArgumentParser(description="Generate ArgoCD Application YAML")
    parser.add_argument("name", help="Application name")
    parser.add_argument("--repo", required=True, help="Git repository URL")
    parser.add_argument("--path", required=True, help="Path in repository")
    parser.add_argument("--revision", default="HEAD", help="Git revision (default: HEAD)")
    parser.add_argument("--dest-namespace", required=True, help="Destination namespace")
    parser.add_argument("--dest-server", default="https://kubernetes.default.svc", help="Destination server")
    parser.add_argument("--project", default="default", help="ArgoCD project")
    parser.add_argument("--namespace", default="argocd", help="ArgoCD namespace")
    parser.add_argument("--auto-sync", action="store_true", help="Enable automated sync")
    parser.add_argument("--helm-chart", help="Helm chart name (for Helm repos)")
    parser.add_argument("--helm-values", action="append", help="Helm values file (can be repeated)")
    parser.add_argument("--helm-set", action="append", help="Helm parameter (name=value, can be repeated)")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    # Parse helm parameters
    helm_params = []
    if args.helm_set:
        for param in args.helm_set:
            if '=' not in param:
                print(f"❌ Invalid helm parameter: {param} (expected name=value)")
                sys.exit(1)
            name, value = param.split('=', 1)
            helm_params.append({'name': name, 'value': value})

    # Generate YAML
    yaml_content = generate_application(
        args.name,
        repo_url=args.repo,
        path=args.path,
        revision=args.revision,
        dest_namespace=args.dest_namespace,
        dest_server=args.dest_server,
        project=args.project,
        namespace=args.namespace,
        auto_sync=args.auto_sync,
        helm_chart=args.helm_chart,
        helm_values=args.helm_values,
        helm_params=helm_params if helm_params else None,
    )

    # Output
    if args.output:
        Path(args.output).write_text(yaml_content)
        print(f"✅ Application created: {args.output}")
    else:
        print(yaml_content)


if __name__ == "__main__":
    main()
