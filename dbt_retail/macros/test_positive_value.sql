{% test positive_value(model, column_name) %}
{#
    Custom generic test: ensures all values in a column are positive (> 0).
    Usage in schema.yml:
        tests:
          - positive_value
#}

select
    {{ column_name }} as invalid_value,
    count(*) as occurrences
from {{ model }}
where {{ column_name }} <= 0
group by {{ column_name }}
having count(*) > 0

{% endtest %}
