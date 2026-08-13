import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Visualization:
    """Class for creating standard visualizations for the CivicPulse project."""
    
    COLOR_PALETTE = {
        'pothole': '#dc2626',
        'garbage': '#16a34a',
        'streetlight': '#ea580c',
        'water_leakage': '#2563eb',
        'drainage': '#7c3aed',
    }
    BG_COLOR = '#f8fafc'
    PAPER_COLOR = '#ffffff'
    TEXT_COLOR = '#0f172a'
    GRID_COLOR = '#e2e8f0'

    def _apply_theme(self, fig: go.Figure) -> go.Figure:
        """Applies the standard dark theme to a Plotly figure."""
        fig.update_layout(
            paper_bgcolor=self.PAPER_COLOR,
            plot_bgcolor=self.BG_COLOR,
            font=dict(color=self.TEXT_COLOR),
            title_font=dict(color=self.TEXT_COLOR, size=16),
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=self.GRID_COLOR)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=self.GRID_COLOR)
        return fig

    def create_hotspot_map(self, df: pd.DataFrame, lat_col: str = 'latitude', lon_col: str = 'longitude', cluster_col: str = 'cluster_id') -> go.Figure:
        """Creates a geographic map showing complaint hotspots."""
        hover_data = []
        for col in ['category', 'ward_name', 'status']:
            if col in df.columns:
                hover_data.append(col)
                
        # Convert cluster_col to string for discrete coloring if it exists
        df_plot = df.copy()
        if cluster_col in df_plot.columns:
            df_plot[cluster_col] = df_plot[cluster_col].astype(str)
            color_arg = cluster_col
        else:
            color_arg = None

        mean_lat = df[lat_col].mean() if not df.empty else 0
        mean_lon = df[lon_col].mean() if not df.empty else 0

        fig = px.scatter_mapbox(
            df_plot,
            lat=lat_col,
            lon=lon_col,
            color=color_arg,
            hover_data=hover_data,
            title='Geographic Complaint Hotspots',
            mapbox_style='open-street-map',
            zoom=11,
            center=dict(lat=mean_lat, lon=mean_lon),
            height=600,
        )
        fig.update_traces(marker=dict(size=8))
        return self._apply_theme(fig)

    def create_category_breakdown_chart(self, df: pd.DataFrame, category_col: str = 'category') -> go.Figure:
        """Creates a pie chart and bar chart showing complaint category distribution."""
        if category_col not in df.columns:
            return self._apply_theme(go.Figure(layout=dict(title='Complaint Category Distribution')))
            
        counts = df[category_col].value_counts().reset_index()
        counts.columns = [category_col, 'count']
        
        # Apply palette colors
        colors = [self.COLOR_PALETTE.get(cat.lower(), '#95A5A6') for cat in counts[category_col]]

        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'pie'}, {'type': 'bar'}]])

        # Pie chart
        fig.add_trace(
            go.Pie(
                labels=counts[category_col],
                values=counts['count'],
                marker=dict(colors=colors),
                textinfo='percent',
                name='Proportion'
            ),
            row=1, col=1
        )

        # Bar chart
        fig.add_trace(
            go.Bar(
                x=counts[category_col],
                y=counts['count'],
                marker_color=colors,
                name='Count'
            ),
            row=1, col=2
        )

        fig.update_layout(title_text='Complaint Category Distribution', showlegend=False)
        return self._apply_theme(fig)

    def create_resolution_time_trend(self, df: pd.DataFrame, date_col: str = 'complaint_date', resolution_col: str = 'resolution_time_hours') -> go.Figure:
        """Creates a line chart showing monthly average resolution time trend."""
        if date_col not in df.columns or resolution_col not in df.columns:
            return self._apply_theme(go.Figure(layout=dict(title='Monthly Average Resolution Time Trend')))

        # Ensure datetime and resolved status (assuming resolution_time_hours is not null for resolved)
        df_plot = df.dropna(subset=[resolution_col]).copy()
        if df_plot.empty:
            return self._apply_theme(go.Figure(layout=dict(title='Monthly Average Resolution Time Trend')))

        df_plot[date_col] = pd.to_datetime(df_plot[date_col])
        
        # Group by month
        df_plot['month'] = df_plot[date_col].dt.to_period('M')
        monthly_avg = df_plot.groupby('month')[resolution_col].mean().reset_index()
        monthly_avg['month'] = monthly_avg['month'].dt.to_timestamp()
        
        overall_avg = df_plot[resolution_col].mean()

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=monthly_avg['month'],
                y=monthly_avg[resolution_col],
                mode='lines+markers',
                fill='tozeroy',
                line=dict(color='#00B4D8'),
                name='Monthly Avg'
            )
        )

        fig.add_hline(
            y=overall_avg,
            line_dash='dash',
            line_color='#FF4B4B',
            annotation_text=f'Overall Avg: {overall_avg:.2f}h',
            annotation_position='top right'
        )

        fig.update_layout(
            title='Monthly Average Resolution Time Trend',
            yaxis_title='Hours',
            xaxis_title='Month'
        )
        return self._apply_theme(fig)

    def create_ward_comparison_chart(self, df: pd.DataFrame, ward_col: str = 'ward_name', metric_col: str = 'resolution_time_hours') -> go.Figure:
        """Creates a horizontal bar chart comparing wards by complaints and resolution time."""
        if ward_col not in df.columns or metric_col not in df.columns:
            return self._apply_theme(go.Figure(layout=dict(title='Ward-wise Complaint Analysis')))

        ward_stats = df.groupby(ward_col).agg(
            total_complaints=(ward_col, 'count'),
            avg_resolution=(metric_col, 'mean')
        ).reset_index()
        
        ward_stats = ward_stats.sort_values('total_complaints', ascending=True)

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=ward_stats[ward_col],
                x=ward_stats['total_complaints'],
                orientation='h',
                marker=dict(
                    color=ward_stats['avg_resolution'],
                    colorscale='RdYlGn_r', # Red for high resolution time, Green for low
                    colorbar=dict(title='Avg Resolution (hrs)')
                ),
                text=ward_stats['total_complaints'],
                textposition='auto',
                name='Complaints'
            )
        )

        fig.update_layout(
            title='Ward-wise Complaint Analysis',
            xaxis_title='Total Complaints',
            yaxis_title='Ward'
        )
        return self._apply_theme(fig)

    def create_sla_breach_distribution(self, df: pd.DataFrame, breach_col: str = 'sla_breached') -> go.Figure:
        """Creates a grouped bar chart showing SLA breaches by category."""
        category_col = 'category'
        if category_col not in df.columns or breach_col not in df.columns:
            return self._apply_theme(go.Figure(layout=dict(title='SLA Breach Distribution by Category')))

        counts = df.groupby([category_col, breach_col]).size().reset_index(name='count')
        if counts.empty:
            return self._apply_theme(go.Figure(layout=dict(title='SLA Breach Distribution by Category')))
            
        totals = counts.groupby(category_col)['count'].transform('sum')
        counts['percentage'] = (counts['count'] / totals * 100).round(1)

        within_sla = counts[counts[breach_col] == 0]
        breached_sla = counts[counts[breach_col] == 1]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=within_sla[category_col],
                y=within_sla['count'],
                name='Within SLA',
                marker_color='#2ECC71',
                text=within_sla['percentage'].apply(lambda x: f'{x}%'),
                textposition='auto'
            )
        )

        fig.add_trace(
            go.Bar(
                x=breached_sla[category_col],
                y=breached_sla['count'],
                name='SLA Breached',
                marker_color='#E74C3C',
                text=breached_sla['percentage'].apply(lambda x: f'{x}%'),
                textposition='auto'
            )
        )

        fig.update_layout(
            title='SLA Breach Distribution by Category',
            barmode='group',
            xaxis_title='Category',
            yaxis_title='Count'
        )
        return self._apply_theme(fig)
