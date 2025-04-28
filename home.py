from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route("/")
def home():
    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT cs.champ_id, cs.lane_id, c.champ_name, cs.pickrate FROM ChampionStats cs "
        "JOIN (SELECT champ_id, MAX(pickrate) as max_pickrate FROM ChampionStats GROUP BY champ_id) max_stats " 
        "ON cs.champ_id=max_stats.champ_id JOIN Champions c ON cs.champ_id=c.champ_id "
        "WHERE cs.pickrate=max_stats.max_pickrate")
    searchbar = cur.fetchall()
    conn.close()
    return render_template("home.html", searchbar=searchbar)


if __name__ == "__main__":
    app.run(debug=True)