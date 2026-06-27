<!DOCTYPE html>
<html>
<head>
    <title>Rent Roll Dashboard</title>

    <!-- Styling (fixes ugly font + layout + colors) -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
        body {
            background: #f6f7fb;
            font-family: Arial, sans-serif;
        }

        .card {
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .table td, .table th {
            vertical-align: middle;
        }

        .small-muted {
            font-size: 12px;
            color: #6c757d;
        }
    </style>
</head>

<body>

<div class="container-fluid p-4">

    <h3 class="mb-4">Rent Roll Dashboard</h3>

    <div class="row g-4">

        <!-- LEFT: Units -->
        <div class="col-lg-8">

            <div class="card p-3">

                <h5 class="mb-3">Units</h5>

                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Property / Unit</th>
                            <th>Status</th>
                            <th>Rent</th>
                            <th>Last Increase</th>
                            <th>Next Increase Due</th>
                        </tr>
                    </thead>

                    <tbody>
                        {% for unit in units %}
                        <tr>
                            <td>
                                <div><strong>{{ unit.property_name }}</strong></div>
                                <div class="small-muted">{{ unit.unit_name }}</div>
                            </td>

                            <td>{{ unit.status }}</td>
                            <td>${{ unit.rent }}</td>

                            <td>
                                {% if unit.last_increase %}
                                    {{ unit.last_increase.date.strftime('%Y-%m-%d') }}
                                    <div class="small-muted">
                                        {{ "%.1f"|format(unit.last_increase.percent_change) }}%
                                    </div>
                                {% else %}
                                    -
                                {% endif %}
                            </td>

                            <td>
                                {% if unit.next_increase_due %}
                                    {{ unit.next_increase_due.strftime('%Y-%m-%d') }}
                                {% else %}
                                    -
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>

            </div>
        </div>

        <!-- RIGHT: Activity -->
        <div class="col-lg-4">

            <div class="card p-3">

                <h5 class="mb-3">Recent Activity</h5>

                <table class="table table-sm table-striped">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Type</th>
                            <th>Unit</th>
                        </tr>
                    </thead>

                    <tbody>
                        {% for a in activities %}
                        <tr>
                            <td>{{ a.event_date }}</td>
                            <td>{{ a.event_type }}</td>
                            <td>{{ a.property_name }} / {{ a.unit_name }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>

            </div>

        </div>

    </div>

</div>

</body>
</html>
