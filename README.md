# How the program flow should work
CLI → ResilienceBot wrapper → HFLocalClient → FLAN-T5 → Checklist output

#CLI
'''
python -m app.main "My API has intermittent 504 timeouts. Give a troubleshooting checklist."

'''

<script src="https://gist.github.com/anonymousgirl123/5e87f5623d4481993239f317d8c2a067"></script>

