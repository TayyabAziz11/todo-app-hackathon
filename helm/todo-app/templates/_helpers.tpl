{{/*
Expand the name of the chart.
*/}}
{{- define "todo-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-app.labels" -}}
helm.sh/chart: {{ include "todo-app.chart" . }}
{{ include "todo-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Service-specific labels
*/}}
{{- define "todo-app.serviceLabels" -}}
app.kubernetes.io/name: {{ .serviceName }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .serviceName }}
app.kubernetes.io/part-of: todo-app
helm.sh/chart: {{ include "todo-app.chart" .root }}
app.kubernetes.io/managed-by: {{ .root.Release.Service }}
{{- if .root.Chart.AppVersion }}
app.kubernetes.io/version: {{ .root.Chart.AppVersion | quote }}
{{- end }}
{{- end }}

{{/*
Service-specific selector labels
*/}}
{{- define "todo-app.serviceSelectorLabels" -}}
app.kubernetes.io/name: {{ .serviceName }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Dapr annotations
*/}}
{{- define "todo-app.daprAnnotations" -}}
{{- if .root.Values.dapr.enabled }}
dapr.io/enabled: "true"
dapr.io/app-id: {{ .serviceName | quote }}
dapr.io/app-port: {{ .appPort | quote }}
dapr.io/log-level: {{ .root.Values.dapr.logLevel | quote }}
dapr.io/enable-api-logging: "true"
{{- end }}
{{- end }}

{{/*
Resource limits
*/}}
{{- define "todo-app.resources" -}}
requests:
  memory: {{ .Values.resources.requests.memory }}
  cpu: {{ .Values.resources.requests.cpu }}
limits:
  memory: {{ .Values.resources.limits.memory }}
  cpu: {{ .Values.resources.limits.cpu }}
{{- end }}

{{/*
Security context
*/}}
{{- define "todo-app.securityContext" -}}
runAsNonRoot: {{ .Values.securityContext.runAsNonRoot }}
runAsUser: {{ .Values.securityContext.runAsUser }}
fsGroup: {{ .Values.securityContext.fsGroup }}
allowPrivilegeEscalation: {{ .Values.securityContext.allowPrivilegeEscalation }}
capabilities:
  drop:
    {{- range .Values.securityContext.capabilities.drop }}
    - {{ . }}
    {{- end }}
{{- end }}
