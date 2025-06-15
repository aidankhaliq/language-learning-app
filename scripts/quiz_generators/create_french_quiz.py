import pandas as pd
import random

questions_data = [
    # Food & Drinks
    {"Language": "French", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": 'Que signifie "pomme" ?', "Options": ["Un fruit rouge ou vert", "Un légume jaune", "Un type de viande", "Une boisson"], "Correct": "Un fruit rouge ou vert"},
    {"Language": "French", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": 'Que signifie "banane" ?', "Options": ["Un fruit long et jaune", "Un légume rouge", "Un type de pain", "Une boisson sucrée"], "Correct": "Un fruit long et jaune"},
    {"Language": "French", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": 'Que signifie "eau" ?', "Options": ["Un liquide clair que l'on boit", "Un fruit", "Une boisson chaude", "Un type de viande"], "Correct": "Un liquide clair que l'on boit"},
    {"Language": "French", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": 'Que signifie "pain" ?', "Options": ["Un aliment fait de farine, cuit au four", "Un fruit sucré", "Une boisson froide", "Un légume"], "Correct": "Un aliment fait de farine, cuit au four"},
    {"Language": "French", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": 'Que signifie "lait" ?', "Options": ["Une boisson blanche venant des vaches", "Un fruit", "Un type de viande", "Un dessert sucré"], "Correct": "Une boisson blanche venant des vaches"},
    # Animals
    {"Language": "French", "Category": "Animals", "Difficulty": "beginner", "Question": 'Que signifie "chien" ?', "Options": ["Un animal domestique qui aboie", "Un gros chat", "Un oiseau qui vole", "Un poisson dans la mer"], "Correct": "Un animal domestique qui aboie"},
    {"Language": "French", "Category": "Animals", "Difficulty": "beginner", "Question": 'Que signifie "chat" ?', "Options": ["Un petit animal domestique qui miaule", "Un gros animal qui rugit", "Un oiseau qui chante", "Un poisson"], "Correct": "Un petit animal domestique qui miaule"},
    {"Language": "French", "Category": "Animals", "Difficulty": "beginner", "Question": 'Que signifie "oiseau" ?', "Options": ["Un animal avec des ailes qui peut voler", "Un gros animal qui nage", "Un insecte petit", "Un poisson"], "Correct": "Un animal avec des ailes qui peut voler"},
    {"Language": "French", "Category": "Animals", "Difficulty": "beginner", "Question": 'Que signifie "poisson" ?', "Options": ["Un animal qui vit dans l'eau", "Un gros animal terrestre", "Un oiseau qui vole", "Un insecte"], "Correct": "Un animal qui vit dans l'eau"},
    {"Language": "French", "Category": "Animals", "Difficulty": "beginner", "Question": 'Que signifie "cheval" ?', "Options": ["Un grand animal que l'on monte", "Un petit animal comme un chat", "Un oiseau qui vole", "Un animal aquatique"], "Correct": "Un grand animal que l'on monte"},
    # Objects
    {"Language": "French", "Category": "Objects", "Difficulty": "beginner", "Question": 'Que signifie "livre" ?', "Options": ["Quelque chose que l'on lit avec des pages", "Un type de nourriture", "Une boisson", "Un type de chaussure"], "Correct": "Quelque chose que l'on lit avec des pages"},
    {"Language": "French", "Category": "Objects", "Difficulty": "beginner", "Question": 'Que signifie "stylo" ?', "Options": ["Un outil pour écrire", "Un type de nourriture", "Un vêtement", "Une place pour s'asseoir"], "Correct": "Un outil pour écrire"},
    {"Language": "French", "Category": "Objects", "Difficulty": "beginner", "Question": 'Que signifie "chaise" ?', "Options": ["Un meuble pour s'asseoir", "Un aliment", "Un outil pour écrire", "Un sac"], "Correct": "Un meuble pour s'asseoir"},
    {"Language": "French", "Category": "Objects", "Difficulty": "beginner", "Question": 'Que signifie "sac" ?', "Options": ["Quelque chose que l'on utilise pour porter des choses", "Un aliment", "Une boisson", "Un endroit pour dormir"], "Correct": "Quelque chose que l'on utilise pour porter des choses"},
    {"Language": "French", "Category": "Objects", "Difficulty": "beginner", "Question": 'Que signifie "clé" ?', "Options": ["Un petit objet pour ouvrir une serrure", "Un type de fruit", "Une boisson", "Un vêtement"], "Correct": "Un petit objet pour ouvrir une serrure"},
    # Family
    {"Language": "French", "Category": "Family", "Difficulty": "beginner", "Question": 'Que signifie "mère" ?', "Options": ["La parent féminine", "Le parent masculin", "Un frère", "Un ami"], "Correct": "La parent féminine"},
    {"Language": "French", "Category": "Family", "Difficulty": "beginner", "Question": 'Que signifie "père" ?', "Options": ["Le parent masculin", "La parent féminine", "Une sœur", "Un professeur"], "Correct": "Le parent masculin"},
    {"Language": "French", "Category": "Family", "Difficulty": "beginner", "Question": 'Que signifie "frère" ?', "Options": ["Un frère masculin", "Une sœur féminine", "Un parent", "Un ami"], "Correct": "Un frère masculin"},
    {"Language": "French", "Category": "Family", "Difficulty": "beginner", "Question": 'Que signifie "sœur" ?', "Options": ["Une sœur féminine", "Un frère masculin", "Un parent", "Un professeur"], "Correct": "Une sœur féminine"},
    {"Language": "French", "Category": "Family", "Difficulty": "beginner", "Question": 'Que signifie "ami" ?', "Options": ["Une personne avec qui on passe du temps", "Un membre de la famille", "Un inconnu", "Un professeur"], "Correct": "Une personne avec qui on passe du temps"},
    # Colors
    {"Language": "French", "Category": "Colors", "Difficulty": "beginner", "Question": 'De quelle couleur est une "pomme" ?', "Options": ["Rouge ou verte", "Bleue", "Noire", "Jaune"], "Correct": "Rouge ou verte"},
    {"Language": "French", "Category": "Colors", "Difficulty": "beginner", "Question": 'De quelle couleur est le "soleil" ?', "Options": ["Jaune", "Verte", "Pourpre", "Brune"], "Correct": "Jaune"},
    {"Language": "French", "Category": "Colors", "Difficulty": "beginner", "Question": 'De quelle couleur est le "gazon" ?', "Options": ["Verte", "Rouge", "Blanche", "Bleue"], "Correct": "Verte"},
    {"Language": "French", "Category": "Colors", "Difficulty": "beginner", "Question": 'De quelle couleur est le "ciel" par une journée claire ?', "Options": ["Bleue", "Rose", "Noire", "Orange"], "Correct": "Bleue"},
    {"Language": "French", "Category": "Colors", "Difficulty": "beginner", "Question": 'De quelle couleur est la "neige" ?', "Options": ["Blanche", "Rouge", "Bleue", "Jaune"], "Correct": "Blanche"},
    # Numbers
    {"Language": "French", "Category": "Numbers", "Difficulty": "beginner", "Question": 'Que signifie "un" ?', "Options": ["1", "2", "3", "4"], "Correct": "1"},
    {"Language": "French", "Category": "Numbers", "Difficulty": "beginner", "Question": 'Que signifie "cinq" ?', "Options": ["5", "6", "7", "8"], "Correct": "5"},
    {"Language": "French", "Category": "Numbers", "Difficulty": "beginner", "Question": 'Que signifie "dix" ?', "Options": ["10", "9", "11", "12"], "Correct": "10"},
    {"Language": "French", "Category": "Numbers", "Difficulty": "beginner", "Question": 'Que signifie "trois" ?', "Options": ["3", "4", "5", "6"], "Correct": "3"},
    {"Language": "French", "Category": "Numbers", "Difficulty": "beginner", "Question": 'Que signifie "sept" ?', "Options": ["7", "8", "9", "10"], "Correct": "7"},
    # Clothing
    {"Language": "French", "Category": "Clothing", "Difficulty": "beginner", "Question": 'Que signifie "chemise" ?', "Options": ["Un vêtement pour le haut du corps", "Un aliment", "Un type de chaussure", "Un chapeau"], "Correct": "Un vêtement pour le haut du corps"},
    {"Language": "French", "Category": "Clothing", "Difficulty": "beginner", "Question": 'Que signifie "chaussures" ?', "Options": ["Des objets que l'on met sur les pieds", "Un aliment", "Un vêtement", "Un sac"], "Correct": "Des objets que l'on met sur les pieds"},
    {"Language": "French", "Category": "Clothing", "Difficulty": "beginner", "Question": 'Que signifie "chapeau" ?', "Options": ["Un vêtement que l'on porte sur la tête", "Un vêtement pour les jambes", "Des chaussures", "Un sac"], "Correct": "Un vêtement que l'on porte sur la tête"},
    {"Language": "French", "Category": "Clothing", "Difficulty": "beginner", "Question": 'Que signifie "pantalon" ?', "Options": ["Un vêtement pour le bas du corps", "Un aliment", "Une boisson", "Un chapeau"], "Correct": "Un vêtement pour le bas du corps"},
    {"Language": "French", "Category": "Clothing", "Difficulty": "beginner", "Question": 'Que signifie "robe" ?', "Options": ["Un vêtement porté par les femmes/les filles", "Des chaussures", "Un chapeau", "Un sac"], "Correct": "Un vêtement porté par les femmes/les filles"},
    # Actions
    {"Language": "French", "Category": "Actions", "Difficulty": "beginner", "Question": 'Que signifie "courir" ?', "Options": ["Se déplacer rapidement avec les pieds", "Dormir", "Manger", "Écrire"], "Correct": "Se déplacer rapidement avec les pieds"},
    {"Language": "French", "Category": "Actions", "Difficulty": "beginner", "Question": 'Que signifie "manger" ?', "Options": ["Mettre de la nourriture dans la bouche et l'avaler", "Boire", "Dormir", "Courir"], "Correct": "Mettre de la nourriture dans la bouche et l'avaler"},
    {"Language": "French", "Category": "Actions", "Difficulty": "beginner", "Question": 'Que signifie "boire" ?', "Options": ["Prendre des liquides dans la bouche", "Manger", "Dormir", "Écrire"], "Correct": "Prendre des liquides dans la bouche"},
    {"Language": "French", "Category": "Actions", "Difficulty": "beginner", "Question": 'Que signifie "dormir" ?', "Options": ["Fermer les yeux et se reposer", "Courir", "Manger", "Lire"], "Correct": "Fermer les yeux et se reposer"},
    {"Language": "French", "Category": "Actions", "Difficulty": "beginner", "Question": 'Que signifie "lire" ?', "Options": ["Regarder les mots et les comprendre", "Boire", "Courir", "Dormir"], "Correct": "Regarder les mots et les comprendre"},
    # Places
    {"Language": "French", "Category": "Places", "Difficulty": "beginner", "Question": 'Que signifie "école" ?', "Options": ["Un lieu où les élèves apprennent", "Un type de nourriture", "Un endroit pour dormir", "Un lieu pour nager"], "Correct": "Un lieu où les élèves apprennent"},
    {"Language": "French", "Category": "Places", "Difficulty": "beginner", "Question": 'Que signifie "maison" ?', "Options": ["Un lieu où les gens vivent", "Une école", "Un parc", "Un restaurant"], "Correct": "Un lieu où les gens vivent"},
    {"Language": "French", "Category": "Places", "Difficulty": "beginner", "Question": 'Que signifie "parc" ?', "Options": ["Un endroit avec de l'herbe, des arbres et des jeux", "Une école", "Un hôpital", "Un magasin"], "Correct": "Un endroit avec de l'herbe, des arbres et des jeux"},
    {"Language": "French", "Category": "Places", "Difficulty": "beginner", "Question": 'Que signifie "hôpital" ?', "Options": ["Un endroit où les gens vont lorsqu'ils sont malades", "Une école", "Un restaurant", "Un parc"], "Correct": "Un endroit où les gens vont lorsqu'ils sont malades"},
    {"Language": "French", "Category": "Places", "Difficulty": "beginner", "Question": 'Que signifie "restaurant" ?', "Options": ["Un endroit où les gens vont manger", "Une école", "Un hôpital", "Un parc"], "Correct": "Un endroit où les gens vont manger"},
    # Time & Days
    {"Language": "French", "Category": "Time & Days", "Difficulty": "beginner", "Question": 'Que signifie "matin" ?', "Options": ["La période du jour avant midi", "La période du jour après minuit", "Le jour avant aujourd'hui", "Le jour après demain"], "Correct": "La période du jour avant midi"},
    {"Language": "French", "Category": "Time & Days", "Difficulty": "beginner", "Question": 'Que signifie "nuit" ?', "Options": ["Le moment où il fait noir et que l'on dort", "Le matin", "L'après-midi", "Le soir"], "Correct": "Le moment où il fait noir et que l'on dort"},
    {"Language": "French", "Category": "Time & Days", "Difficulty": "beginner", "Question": 'Que signifie "lundi" ?', "Options": ["Le premier jour de la semaine", "Le dernier jour de la semaine", "Le premier jour du mois", "Le premier jour de l'année"], "Correct": "Le premier jour de la semaine"},
    {"Language": "French", "Category": "Time & Days", "Difficulty": "beginner", "Question": 'Que signifie "aujourd\'hui" ?', "Options": ["Le jour actuel", "Hier", "Demain", "La semaine dernière"], "Correct": "Le jour actuel"},
    {"Language": "French", "Category": "Time & Days", "Difficulty": "beginner", "Question": 'Que signifie "année" ?', "Options": ["12 mois (365 jours)", "7 jours", "30 jours", "60 minutes"], "Correct": "12 mois (365 jours)"},
]

def shuffle_options(q):
    options = q["Options"][:]
    correct = q["Correct"]
    random.shuffle(options)
    correct_index = options.index(correct)
    letter = ['a', 'b', 'c', 'd'][correct_index]
    q["Options"] = f"a) {options[0]};b) {options[1]};c) {options[2]};d) {options[3]}"
    q["Correct Answer"] = f"{letter}) {options[correct_index]}"
    return q

questions_data = [shuffle_options(dict(q)) for q in questions_data]
df = pd.DataFrame(questions_data)
df.to_excel('french_quiz_questions.xlsx', index=False) 