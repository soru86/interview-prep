{{- define "nest-js-demo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "nest-js-demo.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "nest-js-demo.labels" -}}
app.kubernetes.io/name: {{ include "nest-js-demo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: api
app.kubernetes.io/environment: {{ .Values.environment }}
{{- end -}}

{{- define "nest-js-demo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nest-js-demo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "nest-js-demo.kafkaBrokers" -}}
{{- if .Values.kafka.brokers -}}
{{- .Values.kafka.brokers -}}
{{- else -}}
kafka:29092
{{- end -}}
{{- end -}}
