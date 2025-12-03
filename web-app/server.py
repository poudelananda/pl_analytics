from flask import Flask, render_template, request
import plotly.express as px
from sql_analytic.sql_queries import get_player_stats, get_team_stats
import pandas as pd

app = Flask(__name__)

@app.route("/player", methods=["GET", "POST"])
def player_tab():
    chart_html = None

    if request.method == "POST":
        player = request.form["player"]
        df = get_player_stats(player)
        avg_shots = df["Sh"].mean()
        fig = px.scatter(
            df,
            x="Date",
            y="Sh",
            color="opponent",
            text="opponent",
            title=f"{player} — Shots Over Time (Colored by Opponent + Average Line)",
        )

        fig.update_traces(textposition="top center", mode="markers+text")
        fig.add_scatter(
            x=df["Date"],
            y=df["Sh"],
            mode="lines",
            line=dict(width=1),
            name="Trend",
            showlegend=True
        )
        fig.add_hline(
            y=avg_shots,
            line_width=2,
            line_dash="dash",
            annotation_text=f"Average Shots ({avg_shots:.2f})",
            annotation_position="top left",
            name="Average"
        )

        chart_html = fig.to_html(full_html=False)

    return render_template("player.html", chart_html=chart_html)

@app.route("/teams", methods=["GET", "POST"])
def teams_tab():
    chart_html = None

    if request.method == "POST":
        team = request.form["team"]

        shots_df, position_shots_df, conceded_df, position_conceded_df  = get_team_stats(team)

        fig1 = px.bar(
            shots_df,
            x="Date",
            y="total_shots",
            title=f"{team} — Shots Against Opponent"
        )

        fig2 = px.bar(
            position_shots_df,
            x="PrimaryPos",
            y="avg_shots",
            error_y="std_dev_shots",
            title=f"{team} — Avg Shots By Position Against Opponents"
        )

        fig3 = px.bar(
            conceded_df,
            x="Date",
            y="total_shots",
            title=f"{team} — Shots Conceded by {team}"
        )

        fig4 = px.bar(
            position_conceded_df,
            x="PrimaryPos",
            y="avg_shots",
            error_y="std_dev_shots",
            title=f"{team} — Avg Shots Conceded By Position"
        )


        chart_html = (
            fig1.to_html(full_html=False) +
            "<hr><br>" +
            fig2.to_html(full_html=False) +
            "<hr><br>" +
            fig3.to_html(full_html=False) +
            "<hr><br>" +
            fig4.to_html(full_html=False)
        )

    return render_template("teams.html", chart_html=chart_html)


@app.route("/")
def home():
    return render_template("home.html", chart_html=None)


if __name__ == "__main__":
    app.run(debug=True)
