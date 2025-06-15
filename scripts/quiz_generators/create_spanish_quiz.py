import pandas as pd

# Define the quiz questions data
questions_data = [
    # Food & Drinks
    {
        "Language": "Spanish",
        "Category": "Food & Drinks",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"manzana\"?",
        "Options": "a) Una fruta roja o verde;b) Una verdura amarilla;c) Un tipo de carne;d) Una bebida",
        "Correct Answer": "a) Una fruta roja o verde"
    },
    {
        "Language": "Spanish",
        "Category": "Food & Drinks",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"plátano\"?",
        "Options": "a) Una verdura roja;b) Una fruta larga y amarilla;c) Un tipo de pan;d) Una bebida dulce",
        "Correct Answer": "b) Una fruta larga y amarilla"
    },
    {
        "Language": "Spanish",
        "Category": "Food & Drinks",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"agua\"?",
        "Options": "a) Una fruta;b) Una bebida caliente;c) Un tipo de carne;d) Un líquido claro que bebemos",
        "Correct Answer": "d) Un líquido claro que bebemos"
    },
    {
        "Language": "Spanish",
        "Category": "Food & Drinks",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"pan\"?",
        "Options": "a) Una fruta dulce;b) Una bebida fría;c) Un alimento hecho de harina y horneado;d) Un tipo de verdura",
        "Correct Answer": "c) Un alimento hecho de harina y horneado"
    },
    {
        "Language": "Spanish",
        "Category": "Food & Drinks",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"leche\"?",
        "Options": "a) Una fruta;b) Un tipo de carne;c) Un postre dulce;d) Una bebida blanca proveniente de las vacas",
        "Correct Answer": "d) Una bebida blanca proveniente de las vacas"
    },
    # Animals
    {
        "Language": "Spanish",
        "Category": "Animals",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"perro\"?",
        "Options": "a) Un animal doméstico que ladra;b) Un gran gato;c) Un pájaro que vuela;d) Un pez en el mar",
        "Correct Answer": "a) Un animal doméstico que ladra"
    },
    {
        "Language": "Spanish",
        "Category": "Animals",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"gato\"?",
        "Options": "a) Un gran animal que ruge;b) Un animal doméstico pequeño que maúlla;c) Un pájaro que canta;d) Un pez",
        "Correct Answer": "b) Un animal doméstico pequeño que maúlla"
    },
    {
        "Language": "Spanish",
        "Category": "Animals",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"pájaro\"?",
        "Options": "a) Un gran animal que nada;b) Un insecto pequeño;c) Un animal con alas que puede volar;d) Un pez",
        "Correct Answer": "c) Un animal con alas que puede volar"
    },
    {
        "Language": "Spanish",
        "Category": "Animals",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"pez\"?",
        "Options": "a) Un gran animal terrestre;b) Un pájaro volador;c) Un insecto;d) Un animal que vive en el agua",
        "Correct Answer": "d) Un animal que vive en el agua"
    },
    {
        "Language": "Spanish",
        "Category": "Animals",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"caballo\"?",
        "Options": "a) Un pequeño animal como un gato;b) Un pájaro volador;c) Un animal acuático;d) Un animal grande que se monta",
        "Correct Answer": "d) Un animal grande que se monta"
    },
    # Objects
    {
        "Language": "Spanish",
        "Category": "Objects",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"libro\"?",
        "Options": "a) Algo que se lee y tiene páginas;b) Un tipo de comida;c) Una bebida;d) Un tipo de zapato",
        "Correct Answer": "a) Algo que se lee y tiene páginas"
    },
    {
        "Language": "Spanish",
        "Category": "Objects",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"pluma\"?",
        "Options": "a) Un tipo de comida;b) Una herramienta para escribir;c) Una prenda de ropa;d) Un lugar para sentarse",
        "Correct Answer": "b) Una herramienta para escribir"
    },
    {
        "Language": "Spanish",
        "Category": "Objects",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"silla\"?",
        "Options": "a) Algo para comer;b) Una herramienta para escribir;c) Un mueble para sentarse;d) Una mochila",
        "Correct Answer": "c) Un mueble para sentarse"
    },
    {
        "Language": "Spanish",
        "Category": "Objects",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"mochila\"?",
        "Options": "a) Una comida;b) Una bebida;c) Un lugar para dormir;d) Algo que se usa para llevar cosas",
        "Correct Answer": "d) Algo que se usa para llevar cosas"
    },
    {
        "Language": "Spanish",
        "Category": "Objects",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"llave\"?",
        "Options": "a) Un tipo de fruta;b) Una bebida;c) Un tipo de ropa;d) Un pequeño objeto usado para abrir cerraduras",
        "Correct Answer": "d) Un pequeño objeto usado para abrir cerraduras"
    },
    # Family
    {
        "Language": "Spanish",
        "Category": "Family",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"madre\"?",
        "Options": "a) Una madre femenina;b) Un padre masculino;c) Un hermano;d) Un amigo",
        "Correct Answer": "a) Una madre femenina"
    },
    {
        "Language": "Spanish",
        "Category": "Family",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"padre\"?",
        "Options": "a) Una madre femenina;b) Un padre masculino;c) Una hermana;d) Un profesor",
        "Correct Answer": "b) Un padre masculino"
    },
    {
        "Language": "Spanish",
        "Category": "Family",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"hermano\"?",
        "Options": "a) Una hermana femenina;b) Un padre;c) Un hermano masculino;d) Un amigo",
        "Correct Answer": "c) Un hermano masculino"
    },
    {
        "Language": "Spanish",
        "Category": "Family",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"hermana\"?",
        "Options": "a) Un hermano masculino;b) Un padre;c) Un profesor;d) Una hermana femenina",
        "Correct Answer": "d) Una hermana femenina"
    },
    {
        "Language": "Spanish",
        "Category": "Family",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"amigo\"?",
        "Options": "a) Un miembro de la familia;b) Un extraño;c) Un profesor;d) Una persona que te gusta y pasas tiempo con ella",
        "Correct Answer": "d) Una persona que te gusta y pasas tiempo con ella"
    },
    # Colors
    {
        "Language": "Spanish",
        "Category": "Colors",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"rojo\"?",
        "Options": "a) El color de una manzana;b) Azul;c) Negra;d) Amarilla",
        "Correct Answer": "a) El color de una manzana"
    },
    {
        "Language": "Spanish",
        "Category": "Colors",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"amarillo\"?",
        "Options": "a) Verde;b) El color del sol;c) Morado;d) Marrón",
        "Correct Answer": "b) El color del sol"
    },
    {
        "Language": "Spanish",
        "Category": "Colors",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"verde\"?",
        "Options": "a) Rojo;b) Blanco;c) El color del césped;d) Azul",
        "Correct Answer": "c) El color del césped"
    },
    {
        "Language": "Spanish",
        "Category": "Colors",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"azul\"?",
        "Options": "a) Rosa;b) Negro;c) Naranja;d) El color del cielo en un día claro",
        "Correct Answer": "d) El color del cielo en un día claro"
    },
    {
        "Language": "Spanish",
        "Category": "Colors",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"blanco\"?",
        "Options": "a) El color de la nieve;b) Roja;c) Azul;d) Amarilla",
        "Correct Answer": "a) El color de la nieve"
    },
    # Numbers
    {
        "Language": "Spanish",
        "Category": "Numbers",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"uno\"?",
        "Options": "a) 1;b) 2;c) 3;d) 4",
        "Correct Answer": "a) 1"
    },
    {
        "Language": "Spanish",
        "Category": "Numbers",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"cinco\"?",
        "Options": "a) 6;b) 5;c) 7;d) 8",
        "Correct Answer": "b) 5"
    },
    {
        "Language": "Spanish",
        "Category": "Numbers",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"diez\"?",
        "Options": "a) 9;b) 11;c) 10;d) 12",
        "Correct Answer": "c) 10"
    },
    {
        "Language": "Spanish",
        "Category": "Numbers",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"tres\"?",
        "Options": "a) 4;b) 5;c) 6;d) 3",
        "Correct Answer": "d) 3"
    },
    {
        "Language": "Spanish",
        "Category": "Numbers",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"siete\"?",
        "Options": "a) 7;b) 8;c) 9;d) 10",
        "Correct Answer": "a) 7"
    },
    # Clothing
    {
        "Language": "Spanish",
        "Category": "Clothing",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"camisa\"?",
        "Options": "a) Ropa para la parte superior del cuerpo;b) Algo para comer;c) Un tipo de zapato;d) Un sombrero",
        "Correct Answer": "a) Ropa para la parte superior del cuerpo"
    },
    {
        "Language": "Spanish",
        "Category": "Clothing",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"zapatos\"?",
        "Options": "a) Algo para beber;b) Cosas que usas en los pies;c) Un tipo de comida;d) Una mochila",
        "Correct Answer": "b) Cosas que usas en los pies"
    },
    {
        "Language": "Spanish",
        "Category": "Clothing",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"sombrero\"?",
        "Options": "a) Ropa para las piernas;b) Zapatos;c) Ropa que se usa en la cabeza;d) Mochilas",
        "Correct Answer": "c) Ropa que se usa en la cabeza"
    },
    {
        "Language": "Spanish",
        "Category": "Clothing",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"pantalones\"?",
        "Options": "a) Algo para comer;b) Una bebida;c) Un sombrero;d) Ropa para la parte inferior del cuerpo",
        "Correct Answer": "d) Ropa para la parte inferior del cuerpo"
    },
    {
        "Language": "Spanish",
        "Category": "Clothing",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"vestido\"?",
        "Options": "a) Un tipo de zapato;b) Un sombrero;c) Una mochila;d) Ropa que usan las mujeres/niñas",
        "Correct Answer": "d) Ropa que usan las mujeres/niñas"
    },
    # Actions
    {
        "Language": "Spanish",
        "Category": "Actions",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"correr\"?",
        "Options": "a) Moverse rápidamente con los pies;b) Dormir;c) Comer;d) Escribir",
        "Correct Answer": "a) Moverse rápidamente con los pies"
    },
    {
        "Language": "Spanish",
        "Category": "Actions",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"comer\"?",
        "Options": "a) Beber;b) Poner comida en la boca y tragarla;c) Dormir;d) Correr",
        "Correct Answer": "b) Poner comida en la boca y tragarla"
    },
    {
        "Language": "Spanish",
        "Category": "Actions",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"beber\"?",
        "Options": "a) Comer;b) Dormir;c) Tomar líquidos en la boca;d) Escribir",
        "Correct Answer": "c) Tomar líquidos en la boca"
    },
    {
        "Language": "Spanish",
        "Category": "Actions",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"dormir\"?",
        "Options": "a) Correr;b) Comer;c) Leer;d) Cerrar los ojos y descansar en la cama",
        "Correct Answer": "d) Cerrar los ojos y descansar en la cama"
    },
    {
        "Language": "Spanish",
        "Category": "Actions",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"leer\"?",
        "Options": "a) Mirar las palabras y entenderlas;b) Beber;c) Correr;d) Dormir",
        "Correct Answer": "a) Mirar las palabras y entenderlas"
    },
    # Places
    {
        "Language": "Spanish",
        "Category": "Places",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"escuela\"?",
        "Options": "a) Un lugar donde los estudiantes aprenden;b) Un tipo de comida;c) Un lugar para dormir;d) Un lugar para nadar",
        "Correct Answer": "a) Un lugar donde los estudiantes aprenden"
    },
    {
        "Language": "Spanish",
        "Category": "Places",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"casa\"?",
        "Options": "a) Una escuela;b) Un lugar donde las personas viven;c) Un parque;d) Un restaurante",
        "Correct Answer": "b) Un lugar donde las personas viven"
    },
    {
        "Language": "Spanish",
        "Category": "Places",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"parque\"?",
        "Options": "a) Una escuela;b) Un hospital;c) Un lugar con césped, árboles y juegos;d) Una tienda",
        "Correct Answer": "c) Un lugar con césped, árboles y juegos"
    },
    {
        "Language": "Spanish",
        "Category": "Places",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"hospital\"?",
        "Options": "a) Una escuela;b) Un restaurante;c) Un parque;d) Un lugar donde las personas van cuando están enfermas",
        "Correct Answer": "d) Un lugar donde las personas van cuando están enfermas"
    },
    {
        "Language": "Spanish",
        "Category": "Places",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"restaurante\"?",
        "Options": "a) Una escuela;b) Un hospital;c) Un parque;d) Un lugar donde las personas van a comer",
        "Correct Answer": "d) Un lugar donde las personas van a comer"
    },
    # Time & Days
    {
        "Language": "Spanish",
        "Category": "Time & Days",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"mañana\"?",
        "Options": "a) El período de tiempo antes del mediodía;b) El período de tiempo después de la medianoche;c) El día antes de hoy;d) El día después de hoy",
        "Correct Answer": "a) El período de tiempo antes del mediodía"
    },
    {
        "Language": "Spanish",
        "Category": "Time & Days",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"noche\"?",
        "Options": "a) El tiempo cuando está claro y la gente despierta;b) El tiempo cuando está oscuro y la gente duerme;c) El día antes de ayer;d) El día después de mañana",
        "Correct Answer": "b) El tiempo cuando está oscuro y la gente duerme"
    },
    {
        "Language": "Spanish",
        "Category": "Time & Days",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"lunes\"?",
        "Options": "a) El último día de la semana;b) El último día del mes;c) El primer día de la semana;d) El primer día del mes",
        "Correct Answer": "c) El primer día de la semana"
    },
    {
        "Language": "Spanish",
        "Category": "Time & Days",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"hoy\"?",
        "Options": "a) El día de ayer;b) El día de mañana;c) El día de la semana pasada;d) El día actual",
        "Correct Answer": "d) El día actual"
    },
    {
        "Language": "Spanish",
        "Category": "Time & Days",
        "Difficulty": "beginner",
        "Question": "¿Qué significa \"año\"?",
        "Options": "a) 7 días;b) 30 días;c) 60 minutos;d) 12 meses (365 días)",
        "Correct Answer": "d) 12 meses (365 días)"
    }
]

# Create DataFrame
df = pd.DataFrame(questions_data)

# Save to Excel
df.to_excel('spanish_quiz_questions.xlsx', index=False)
print("Excel file 'spanish_quiz_questions.xlsx' has been created successfully with 50 questions.") 