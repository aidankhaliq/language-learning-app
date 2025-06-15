import pandas as pd
import random

questions_data = [
    # Food & Drinks
    {"Language": "Portuguese", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": 'O que significa "maçã"?', "Options": ["Uma fruta vermelha ou verde", "Um vegetal amarelo", "Um tipo de carne", "Uma bebida"], "Correct": "Uma fruta vermelha ou verde"},
    {"Language": "Portuguese", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": 'O que significa "banana"?', "Options": ["Uma fruta longa e amarela", "Um vegetal vermelho", "Um tipo de pão", "Uma bebida doce"], "Correct": "Uma fruta longa e amarela"},
    {"Language": "Portuguese", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": 'O que significa "água"?', "Options": ["Um líquido claro que bebemos", "Uma fruta", "Uma bebida quente", "Um tipo de carne"], "Correct": "Um líquido claro que bebemos"},
    {"Language": "Portuguese", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": 'O que significa "pão"?', "Options": ["Um alimento feito de farinha e assado", "Uma fruta doce", "Uma bebida fria", "Um tipo de legume"], "Correct": "Um alimento feito de farinha e assado"},
    {"Language": "Portuguese", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": 'O que significa "leite"?', "Options": ["Uma bebida branca de vaca", "Uma fruta", "Um tipo de carne", "Uma sobremesa doce"], "Correct": "Uma bebida branca de vaca"},
    # Animals
    {"Language": "Portuguese", "Category": "Animals", "Difficulty": "beginner", "Question": 'O que significa "cachorro"?', "Options": ["Um animal de estimação que late", "Um grande gato", "Um pássaro que voa", "Um peixe no mar"], "Correct": "Um animal de estimação que late"},
    {"Language": "Portuguese", "Category": "Animals", "Difficulty": "beginner", "Question": 'O que significa "gato"?', "Options": ["Um pequeno animal de estimação que mia", "Um grande animal que ruge", "Um pássaro que canta", "Um peixe"], "Correct": "Um pequeno animal de estimação que mia"},
    {"Language": "Portuguese", "Category": "Animals", "Difficulty": "beginner", "Question": 'O que significa "pássaro"?', "Options": ["Um animal com asas que pode voar", "Um grande animal que nada", "Um inseto pequeno", "Um peixe"], "Correct": "Um animal com asas que pode voar"},
    {"Language": "Portuguese", "Category": "Animals", "Difficulty": "beginner", "Question": 'O que significa "peixe"?', "Options": ["Um animal que vive na água", "Um grande animal terrestre", "Um pássaro voador", "Um inseto"], "Correct": "Um animal que vive na água"},
    {"Language": "Portuguese", "Category": "Animals", "Difficulty": "beginner", "Question": 'O que significa "cavalo"?', "Options": ["Um grande animal usado para montar", "Um pequeno animal como um gato", "Um pássaro que voa", "Um animal aquático"], "Correct": "Um grande animal usado para montar"},
    # Objects
    {"Language": "Portuguese", "Category": "Objects", "Difficulty": "beginner", "Question": 'O que significa "livro"?', "Options": ["Algo que você lê com páginas", "Um tipo de comida", "Uma bebida", "Um tipo de sapato"], "Correct": "Algo que você lê com páginas"},
    {"Language": "Portuguese", "Category": "Objects", "Difficulty": "beginner", "Question": 'O que significa "caneta"?', "Options": ["Uma ferramenta para escrever", "Um tipo de comida", "Uma peça de roupa", "Um lugar para sentar"], "Correct": "Uma ferramenta para escrever"},
    {"Language": "Portuguese", "Category": "Objects", "Difficulty": "beginner", "Question": 'O que significa "cadeira"?', "Options": ["Um móvel para sentar", "Uma comida", "Uma ferramenta para escrever", "Uma mochila"], "Correct": "Um móvel para sentar"},
    {"Language": "Portuguese", "Category": "Objects", "Difficulty": "beginner", "Question": 'O que significa "mochila"?', "Options": ["Algo usado para carregar coisas", "Uma comida", "Uma bebida", "Um lugar para dormir"], "Correct": "Algo usado para carregar coisas"},
    {"Language": "Portuguese", "Category": "Objects", "Difficulty": "beginner", "Question": 'O que significa "chave"?', "Options": ["Um pequeno objeto para abrir fechaduras", "Um tipo de fruta", "Uma bebida", "Uma peça de roupa"], "Correct": "Um pequeno objeto para abrir fechaduras"},
    # Family
    {"Language": "Portuguese", "Category": "Family", "Difficulty": "beginner", "Question": 'O que significa "mãe"?', "Options": ["A parenta feminina", "O pai masculino", "Um irmão", "Um amigo"], "Correct": "A parenta feminina"},
    {"Language": "Portuguese", "Category": "Family", "Difficulty": "beginner", "Question": 'O que significa "pai"?', "Options": ["O parenta masculino", "A mãe feminina", "Uma irmã", "Um professor"], "Correct": "O parenta masculino"},
    {"Language": "Portuguese", "Category": "Family", "Difficulty": "beginner", "Question": 'O que significa "irmão"?', "Options": ["Um irmão masculino", "Uma irmã feminina", "Um pai", "Um amigo"], "Correct": "Um irmão masculino"},
    {"Language": "Portuguese", "Category": "Family", "Difficulty": "beginner", "Question": 'O que significa "irmã"?', "Options": ["Uma irmã feminina", "Um irmão masculino", "Um pai", "Um professor"], "Correct": "Uma irmã feminina"},
    {"Language": "Portuguese", "Category": "Family", "Difficulty": "beginner", "Question": 'O que significa "amigo"?', "Options": ["Uma pessoa com quem você passa tempo", "Um membro da família", "Um estranho", "Um professor"], "Correct": "Uma pessoa com quem você passa tempo"},
    # Colors
    {"Language": "Portuguese", "Category": "Colors", "Difficulty": "beginner", "Question": 'De que cor é uma "maçã"?', "Options": ["Vermelha ou verde", "Azul", "Preta", "Amarela"], "Correct": "Vermelha ou verde"},
    {"Language": "Portuguese", "Category": "Colors", "Difficulty": "beginner", "Question": 'De que cor é o "sol"?', "Options": ["Amarelo", "Verde", "Roxo", "Marrom"], "Correct": "Amarelo"},
    {"Language": "Portuguese", "Category": "Colors", "Difficulty": "beginner", "Question": 'De que cor é a "grama"?', "Options": ["Verde", "Vermelha", "Branca", "Azul"], "Correct": "Verde"},
    {"Language": "Portuguese", "Category": "Colors", "Difficulty": "beginner", "Question": 'De que cor é o "céu" em um dia claro?', "Options": ["Azul", "Rosa", "Preto", "Laranja"], "Correct": "Azul"},
    {"Language": "Portuguese", "Category": "Colors", "Difficulty": "beginner", "Question": 'De que cor é a "neve"?', "Options": ["Branca", "Vermelha", "Azul", "Amarela"], "Correct": "Branca"},
    # Numbers
    {"Language": "Portuguese", "Category": "Numbers", "Difficulty": "beginner", "Question": 'O que significa "um"?', "Options": ["1", "2", "3", "4"], "Correct": "1"},
    {"Language": "Portuguese", "Category": "Numbers", "Difficulty": "beginner", "Question": 'O que significa "cinco"?', "Options": ["5", "6", "7", "8"], "Correct": "5"},
    {"Language": "Portuguese", "Category": "Numbers", "Difficulty": "beginner", "Question": 'O que significa "dez"?', "Options": ["10", "9", "11", "12"], "Correct": "10"},
    {"Language": "Portuguese", "Category": "Numbers", "Difficulty": "beginner", "Question": 'O que significa "três"?', "Options": ["3", "4", "5", "6"], "Correct": "3"},
    {"Language": "Portuguese", "Category": "Numbers", "Difficulty": "beginner", "Question": 'O que significa "sete"?', "Options": ["7", "8", "9", "10"], "Correct": "7"},
    # Clothing
    {"Language": "Portuguese", "Category": "Clothing", "Difficulty": "beginner", "Question": 'O que significa "camisa"?', "Options": ["Uma roupa para a parte superior do corpo", "Uma comida", "Um tipo de sapato", "Um chapéu"], "Correct": "Uma roupa para a parte superior do corpo"},
    {"Language": "Portuguese", "Category": "Clothing", "Difficulty": "beginner", "Question": 'O que significa "sapatos"?', "Options": ["Coisas que você usa nos pés", "Algo para comer", "Uma roupa", "Uma mochila"], "Correct": "Coisas que você usa nos pés"},
    {"Language": "Portuguese", "Category": "Clothing", "Difficulty": "beginner", "Question": 'O que significa "chapéu"?', "Options": ["Uma roupa que você usa na cabeça", "Uma roupa para as pernas", "Sapatos", "Uma mochila"], "Correct": "Uma roupa que você usa na cabeça"},
    {"Language": "Portuguese", "Category": "Clothing", "Difficulty": "beginner", "Question": 'O que significa "calças"?', "Options": ["Roupas para a parte inferior do corpo", "Uma comida", "Uma bebida", "Um chapéu"], "Correct": "Roupas para a parte inferior do corpo"},
    {"Language": "Portuguese", "Category": "Clothing", "Difficulty": "beginner", "Question": 'O que significa "vestido"?', "Options": ["Uma roupa que mulheres/meninas usam", "Sapatos", "Um chapéu", "Uma mochila"], "Correct": "Uma roupa que mulheres/meninas usam"},
    # Actions
    {"Language": "Portuguese", "Category": "Actions", "Difficulty": "beginner", "Question": 'O que significa "correr"?', "Options": ["Mover-se rapidamente com os pés", "Dormir", "Comer", "Escrever"], "Correct": "Mover-se rapidamente com os pés"},
    {"Language": "Portuguese", "Category": "Actions", "Difficulty": "beginner", "Question": 'O que significa "comer"?', "Options": ["Colocar comida na boca e engolir", "Beber", "Dormir", "Correr"], "Correct": "Colocar comida na boca e engolir"},
    {"Language": "Portuguese", "Category": "Actions", "Difficulty": "beginner", "Question": 'O que significa "beber"?', "Options": ["Tomar líquidos na boca", "Comer", "Dormir", "Escrever"], "Correct": "Tomar líquidos na boca"},
    {"Language": "Portuguese", "Category": "Actions", "Difficulty": "beginner", "Question": 'O que significa "dormir"?', "Options": ["Fechar os olhos e descansar", "Correr", "Comer", "Ler"], "Correct": "Fechar os olhos e descansar"},
    {"Language": "Portuguese", "Category": "Actions", "Difficulty": "beginner", "Question": 'O que significa "ler"?', "Options": ["Olhar as palavras e entendê-las", "Beber", "Correr", "Dormir"], "Correct": "Olhar as palavras e entendê-las"},
    # Places
    {"Language": "Portuguese", "Category": "Places", "Difficulty": "beginner", "Question": 'O que significa "escola"?', "Options": ["Um lugar onde os alunos aprendem", "Um tipo de comida", "Um lugar para dormir", "Um lugar para nadar"], "Correct": "Um lugar onde os alunos aprendem"},
    {"Language": "Portuguese", "Category": "Places", "Difficulty": "beginner", "Question": 'O que significa "casa"?', "Options": ["Um lugar onde as pessoas vivem", "Uma escola", "Um parque", "Um restaurante"], "Correct": "Um lugar onde as pessoas vivem"},
    {"Language": "Portuguese", "Category": "Places", "Difficulty": "beginner", "Question": 'O que significa "parque"?', "Options": ["Um lugar com grama, árvores e brinquedos", "Uma escola", "Um hospital", "Uma loja"], "Correct": "Um lugar com grama, árvores e brinquedos"},
    {"Language": "Portuguese", "Category": "Places", "Difficulty": "beginner", "Question": 'O que significa "hospital"?', "Options": ["Um lugar onde as pessoas vão quando estão doentes", "Uma escola", "Um restaurante", "Um parque"], "Correct": "Um lugar onde as pessoas vão quando estão doentes"},
    {"Language": "Portuguese", "Category": "Places", "Difficulty": "beginner", "Question": 'O que significa "restaurante"?', "Options": ["Um lugar onde as pessoas vão para comer", "Uma escola", "Um hospital", "Um parque"], "Correct": "Um lugar onde as pessoas vão para comer"},
    # Time & Days
    {"Language": "Portuguese", "Category": "Time & Days", "Difficulty": "beginner", "Question": 'O que significa "manhã"?', "Options": ["A parte do dia antes do meio-dia", "A parte do dia depois da meia-noite", "O dia anterior ao de hoje", "O dia depois de amanhã"], "Correct": "A parte do dia antes do meio-dia"},
    {"Language": "Portuguese", "Category": "Time & Days", "Difficulty": "beginner", "Question": 'O que significa "noite"?', "Options": ["O período em que está escuro e as pessoas dormem", "A manhã", "A tarde", "O fim da tarde"], "Correct": "O período em que está escuro e as pessoas dormem"},
    {"Language": "Portuguese", "Category": "Time & Days", "Difficulty": "beginner", "Question": 'O que significa "segunda-feira"?', "Options": ["O primeiro dia da semana", "O último dia da semana", "O primeiro dia do mês", "O primeiro dia do ano"], "Correct": "O primeiro dia da semana"},
    {"Language": "Portuguese", "Category": "Time & Days", "Difficulty": "beginner", "Question": 'O que significa "hoje"?', "Options": ["O dia atual", "Ontem", "Amanhã", "A semana passada"], "Correct": "O dia atual"},
    {"Language": "Portuguese", "Category": "Time & Days", "Difficulty": "beginner", "Question": 'O que significa "ano"?', "Options": ["12 meses (365 dias)", "7 dias", "30 dias", "60 minutos"], "Correct": "12 meses (365 dias)"},
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
df.to_excel('portuguese_quiz_questions.xlsx', index=False) 