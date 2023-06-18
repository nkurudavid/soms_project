from plotly.subplots import make_subplots
import plotly.graph_objects as go

def generate_pie_chart(trainees):
    # Count trainees by stack and cohort
    stack_cohort_counts = {}

    for trainee in trainees:
        stack_name = trainee.stack.name
        cohort_name = trainee.cohort.cohort_name

        if stack_name not in stack_cohort_counts:
            stack_cohort_counts[stack_name] = {}

        if cohort_name not in stack_cohort_counts[stack_name]:
            stack_cohort_counts[stack_name][cohort_name] = 0

        stack_cohort_counts[stack_name][cohort_name] += 1

    # Prepare data for the pie chart
    data = []
    labels = []
    colors = []
    count = 0

    for stack_name, cohort_counts in stack_cohort_counts.items():
        for cohort_name, trainee_count in cohort_counts.items():
            count += trainee_count
            labels.append(f"{stack_name} - {cohort_name}")
            colors.append(f"hsl({(count * 40) % 360}, 50%, 50%)")  # Generate colors

            data.append(trainee_count)

    # Create the pie chart
    fig = make_subplots(rows=1, cols=1, specs=[[{"type": "pie"}]])

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=data,
            marker=dict(colors=colors),
            hoverinfo="label+percent",
            textinfo="value",
            textfont=dict(size=12),
        ),
        row=1,
        col=1,
    )

    fig.update_layout(title="Trainees by Stack and Cohort")

    return fig
