@app.function_name(name="DailyERPAnomalyCheck")
@app.schedule(schedule="0 0 * * *", arg_name="timer", run_on_startup=False)
def daily_anomaly(timer):
    ai = AskERP_AI()
    report = ai.process_user_query("run anomaly check")
    # send email / Teams / dashboard
