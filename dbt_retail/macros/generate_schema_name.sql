{% macro generate_schema_name(custom_schema_name, node) -%}
    {#
        Override default dbt schema naming.
        Instead of: public_silver, public_gold
        We get:     silver, gold
    #}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
