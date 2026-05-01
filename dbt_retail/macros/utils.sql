{% macro cents_to_dollars(column_name, precision=2) %}
    round({{ column_name }}::numeric / 100, {{ precision }})
{% endmacro %}

{% macro calculate_gross_margin(revenue_col, cost_col) %}
    case
        when {{ revenue_col }} > 0
        then round((({{ revenue_col }} - {{ cost_col }}) / {{ revenue_col }}) * 100, 2)
        else 0
    end
{% endmacro %}
