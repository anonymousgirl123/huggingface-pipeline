# How the program flow should work
CLI → ResilienceBot wrapper → HFLocalClient → FLAN-T5 → Checklist output

#CLI
'''
python -m app.main "My API has intermittent 504 timeouts. Give a troubleshooting checklist."

'''

