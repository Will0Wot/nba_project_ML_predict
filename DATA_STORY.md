# NBA Matchup Prediction Storyboard

The visualization suite in this repository highlights how the current dataset captures the flow of the 2022 season for the Milwaukee Bucks, Toronto Raptors, Phoenix Suns, Miami Heat, Memphis Grizzlies, and a handful of other teams. Together, the figures give you a concise narrative you can share with stakeholders before diving into the predictive engine.

![Offense vs. Defense](reports/figures/team_offense_defense.png)

## 1. Establish the landscape
* **Milwaukee's scoring punch:** The Bucks average just over 33 points in the tracked logs while holding opponents to roughly 14.6 points, producing an elite +18.6 net rating in this slice of data. That dominant two-way profile makes them the clear benchmark for anyone simulating postseason matchups.
* **Crowded middle class:** Toronto, Phoenix, and Miami cluster together with modest offensive outputs (18–20 points) and similarly sturdy defenses (allowing 13–17 points). Their net ratings between +2.5 and +5 points suggest games that hinge on execution rather than talent gaps.
* **Memphis as a disruptor:** Despite scoring only 14.0 points per game in this sample, Memphis nearly breaks even thanks to a defense that keeps opponents to 13.8 points. The Grizzlies' grinding style is a reminder to weigh pace and turnover battles when projecting matchups.

![Home court advantage](reports/figures/home_court_advantage.png)

## 2. Emphasize context with home court dynamics
* **The Grindhouse effect:** Memphis enjoys the league’s steepest home lift, winning 85.7% of their home games compared with 27.3% on the road. That 58-point swing underscores how FedExForum energy amplifies their defensive identity.
* **Heat culture travels—barely:** Miami and Toronto also post 40-point-plus home edges, so analysts should bump their win probabilities materially when those teams play in front of their own fans.
* **Watch for small samples:** Because the dataset only includes the logs we were able to extract, some teams may not appear or may have limited road/home splits. Use the charts to flag where you need fresh data pulls before making hard commitments.

![Top scorers](reports/figures/top_scorers.png)

## 3. Spotlight the player engines
* **Giannis sets the ceiling:** Giannis Antetokounmpo's 31.1 points in just 32.2 minutes per game anchor Milwaukee’s offense. In simulations, his availability and foul trouble assumptions will swing the Bucks' projections dramatically.
* **Bam drives Miami’s versatility:** Bam Adebayo delivers 20.4 points across 75 tracked games, reminding us that Miami’s half-court offense runs through his handoffs and short-roll decisions.
* **Supporting stars:** Deandre Ayton, OG Anunoby, and Jarrett Allen fall in the 14–18 point range while logging heavy minutes. Their production profiles help you reason about matchup-specific props—think rebound totals for Allen or corner threes for Anunoby when defenses collapse on primary options.

![Ball security and movement](reports/figures/assist_turnover_balance.png)

## 4. Tie style to outcomes
* **Sharing the ball:** Milwaukee and Miami convert high assist numbers into efficient offense while keeping turnovers manageable, sitting at the favorable upper-left portion of the scatter.
* **Decision pressure points:** Teams closer to the diagonal (e.g., Phoenix and Memphis) operate with thinner margins—forcing turnovers or neutralizing assist hubs becomes a practical coaching lever in your matchup models.

## 5. Limitations and next steps
* **Partial season snapshot:** The sample currently spans 20–25 games per team and excludes several franchises entirely. Treat the charts as directional until you expand coverage.
* **Missing advanced stats:** Pace, true shooting, and lineup combinations are not yet encoded. Adding them will enrich both the visuals and the predictive features.
* **Re-run visuals after updates:** Whenever you pull fresh player logs or retrain the model, regenerate the figures via `python -m nba_predictor.visualization --player-logs <path_to_csv>` so the story stays aligned with the data powering the engine.

With these visuals, you can articulate why the model leans toward Milwaukee in neutral settings, how home courts reshape probabilities, and which player matchups deserve the most scrutiny when crafting betting strategies or preview packages. Run `python -m nba_predictor.visualization --player-logs player_game_logs_2022.csv --pdf reports/summary.pdf` to generate a shareable PDF that stitches this story together with the charts. The resulting file lives in the git-ignored `reports/` directory, so regenerate it locally whenever you refresh the dataset.

# NBA Matchup Story (Simple, Plain-English)

These pictures tell a simple story about part of the 2022 season for a handful of teams (Bucks, Raptors, Suns, Heat, Grizzlies, and a few others). You don’t need any technical background—just use the quick “what to look for” notes under each chart.

---

![Offense vs. Defense](reports/figures/team_offense_defense.png)

## 1) Who looks strongest overall?
**What the chart shows:** Each dot is a team.
- Farther **right** = scores more points.
- Farther **down** = gives up fewer points.
- Brighter color = usually wins by more.

**What to look for:**
- **Milwaukee Bucks** stand out. In this sample of games, they score about **33** and allow about **15**, so they typically win by a lot.
- **Raptors, Suns, and Heat** are solid on both sides of the ball and cluster near the middle—good, competitive teams.
- **Grizzlies** don’t score much (~14) but also don’t allow much (~14), so many of their games are tight.

---

![Home court advantage](reports/figures/home_court_advantage.png)

## 2) How much does playing at home help?
**What the chart shows:** The size of the bar is how much better a team’s **home** record is than its **road** record.

**What to look for:**
- **Memphis** gets the biggest boost at home (a huge swing compared with their road games). Home crowd = real advantage for them.
- **Miami** and **Toronto** also see strong bumps at home. When they play in their own arena, give them extra credit.

---

![Top scorers](reports/figures/top_scorers.png)

## 3) Who drives the scoring?
**What the chart shows:** Players with the highest average points per game in our data.

**What to look for:**
- **Giannis Antetokounmpo** leads the group at about **31** points (in ~32 minutes). If he’s playing, Milwaukee’s offense gets a big lift.
- **Bam Adebayo** is a steady scorer (~20) and a key piece of Miami’s offense.
- **Deandre Ayton, OG Anunoby, Jarrett Allen** and others add reliable points for their teams.

---

![Ball security and movement](reports/figures/assist_turnover_balance.png)

## 4) Do teams share the ball and avoid mistakes?
**What the chart shows:** Where teams land on **assists** (sharing the ball) vs **turnovers** (mistakes that give the ball away).

**What to look for:**
- Best spot is the **upper-left**: more assists, fewer turnovers. **Milwaukee** and **Miami** live near that zone.
- Teams closer to the middle (like **Phoenix** or **Memphis**) have thinner margins—forcing turnovers or disrupting passes can swing a game.

---

## Important notes
- This is a **partial snapshot** of the season (some teams have fewer games logged), so treat it as a helpful guide—not a full league ranking.
- We haven’t added deeper stats yet (like pace or shot quality). Adding those later will make the story even clearer.

---

## Where to find or refresh the pictures
- The charts save to `reports/figures/`.
- If you’re helping maintain this project and need to refresh the images after updating the data, you can run:

```bash
python -m nba_predictor.visualization --player-logs player_game_logs_2022.csv --pdf reports/summary.pdf
```

This creates updated PNGs in `reports/figures/` and (optionally) a shareable PDF in `reports/summary.pdf`.