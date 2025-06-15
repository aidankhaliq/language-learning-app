import pandas as pd
import random

questions_data = [
    # Food & Drinks
    {"Language": "Tamil", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": '"ஆப்பிள்" (āppiḷ) என்ன அர்த்தம்?', "Options": ["சிவப்பு அல்லது பச்சை பழம்", "மஞ்சள் காய்கறி", "இறைச்சி", "பானம்"], "Correct": "சிவப்பு அல்லது பச்சை பழம்"},
    {"Language": "Tamil", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": '"வாழைப்பழம்" (vāḻaippaḻam) என்ன அர்த்தம்?', "Options": ["நீளமான மஞ்சள் பழம்", "சிவப்பு காய்கறி", "ரொட்டி", "இனிப்பான பானம்"], "Correct": "நீளமான மஞ்சள் பழம்"},
    {"Language": "Tamil", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": '"நீர்" (nīr) என்ன அர்த்தம்?', "Options": ["பரிபூரணமாகக் குடிக்கப்படும் தண்ணீர்", "பழம்", "வெப்பமான பானம்", "இறைச்சி"], "Correct": "பரிபூரணமாகக் குடிக்கப்படும் தண்ணீர்"},
    {"Language": "Tamil", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": '"ரொட்டி" (roṭṭi) என்ன அர்த்தம்?', "Options": ["மாவு கொண்டு தயாரிக்கப்படும் உணவு", "இனிப்பு பழம்", "குளிர்பானம்", "காய்கறி"], "Correct": "மாவு கொண்டு தயாரிக்கப்படும் உணவு"},
    {"Language": "Tamil", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": '"பால்" (pāl) என்ன அர்த்தம்?', "Options": ["மாடு பால்", "பழம்", "இறைச்சி", "இனிப்பான டிசெர்ட்"], "Correct": "மாடு பால்"},
    # Animals
    {"Language": "Tamil", "Category": "Animals", "Difficulty": "beginner", "Question": '"நாய்" (nāy) என்ன அர்த்தம்?', "Options": ["வழக்கமான வீட்டு பிராணி", "பெரிய பூனை", "பறக்கும் பறவை", "கடலில் வாழும் மீன்"], "Correct": "வழக்கமான வீட்டு பிராணி"},
    {"Language": "Tamil", "Category": "Animals", "Difficulty": "beginner", "Question": '"பூனை" (pūṇai) என்ன அர்த்தம்?', "Options": ["சிறிய வீட்டு பிராணி", "பெரிய பூனை", "பறக்கும் பறவை", "மீன்"], "Correct": "சிறிய வீட்டு பிராணி"},
    {"Language": "Tamil", "Category": "Animals", "Difficulty": "beginner", "Question": '"பறவை" (paṟavai) என்ன அர்த்தம்?', "Options": ["பறக்கக் கூடிய பறவை", "பெரிய நீர்க்கடலில் வாழும் பிராணி", "சிறிய சிறுகுஞ்சு", "மீன்"], "Correct": "பறக்கக் கூடிய பறவை"},
    {"Language": "Tamil", "Category": "Animals", "Difficulty": "beginner", "Question": '"மீன்" (mīṉ) என்ன அர்த்தம்?', "Options": ["தண்ணீரில் வாழும் உயிரினம்", "பெரிய நிலப் பிராணி", "பறக்கும் பறவை", "சிறிய சிறுகுஞ்சு"], "Correct": "தண்ணீரில் வாழும் உயிரினம்"},
    {"Language": "Tamil", "Category": "Animals", "Difficulty": "beginner", "Question": '"குதிரை" (kuthirai) என்ன அர்த்தம்?', "Options": ["சவாரி செய்ய பயன்படுத்தப்படும் பெரிய பிராணி", "பூனை மாதிரியான சிறிய பிராணி", "பறக்கும் பறவை", "கடல் பிராணி"], "Correct": "சவாரி செய்ய பயன்படுத்தப்படும் பெரிய பிராணி"},
    # Everyday Objects
    {"Language": "Tamil", "Category": "Objects", "Difficulty": "beginner", "Question": '"புத்தகம்" (puththakam) என்ன அர்த்தம்?', "Options": ["நீங்கள் படிக்க பயன்படும் பொருள்", "உணவு", "பானம்", "காலணிகள்"], "Correct": "நீங்கள் படிக்க பயன்படும் பொருள்"},
    {"Language": "Tamil", "Category": "Objects", "Difficulty": "beginner", "Question": '"பென்சில்" (penṡil) என்ன அர்த்தம்?', "Options": ["எழுத உதவும் கருவி", "உணவு", "உடைகள்", "இருக்கை"], "Correct": "எழுத உதவும் கருவி"},
    {"Language": "Tamil", "Category": "Objects", "Difficulty": "beginner", "Question": '"சிங்கம்" (ciṅkam) என்ன அர்த்தம்?', "Options": ["உட்கார்வதற்கு பயன்படும் பொருள்", "உணவு", "எழுதுதல்", "ஒரு பையில் வைக்கப்படுகிறது"], "Correct": "உட்கார்வதற்கு பயன்படும் பொருள்"},
    {"Language": "Tamil", "Category": "Objects", "Difficulty": "beginner", "Question": '"பேக்" (pēk) என்ன அர்த்தம்?', "Options": ["பொருட்களை எடுத்து செல்லும் பொருள்", "உணவு", "பானம்", "தூக்கம்"], "Correct": "பொருட்களை எடுத்து செல்லும் பொருள்"},
    {"Language": "Tamil", "Category": "Objects", "Difficulty": "beginner", "Question": '"சாவி" (cāvi) என்ன அர்த்தம்?', "Options": ["பூட்டுகளை திறக்க பயன்படுத்தப்படும் சிறிய கருவி", "பழம்", "பானம்", "உடைகள்"], "Correct": "பூட்டுகளை திறக்க பயன்படுத்தப்படும் சிறிய கருவி"},
    # Family & People
    {"Language": "Tamil", "Category": "Family", "Difficulty": "beginner", "Question": '"தாய்" (tāy) என்ன அர்த்தம்?', "Options": ["பெண் பெற்றோர்", "ஆண் பெற்றோர்", "சகோதரர்", "நண்பர்"], "Correct": "பெண் பெற்றோர்"},
    {"Language": "Tamil", "Category": "Family", "Difficulty": "beginner", "Question": '"பிதா" (pitā) என்ன அர்த்தம்?', "Options": ["ஆண் பெற்றோர்", "பெண் பெற்றோர்", "சகோதரி", "ஆசிரியர்"], "Correct": "ஆண் பெற்றோர்"},
    {"Language": "Tamil", "Category": "Family", "Difficulty": "beginner", "Question": '"அண்ணன்" (aṇṇan) என்ன அர்த்தம்?', "Options": ["ஆண் சகோதரர்", "பெண் சகோதரி", "பெற்றோர்", "நண்பர்"], "Correct": "ஆண் சகோதரர்"},
    {"Language": "Tamil", "Category": "Family", "Difficulty": "beginner", "Question": '"தங்கை" (taṅkai) என்ன அர்த்தம்?', "Options": ["பெண் சகோதரி", "ஆண் சகோதரர்", "பெற்றோர்", "ஆசிரியர்"], "Correct": "பெண் சகோதரி"},
    {"Language": "Tamil", "Category": "Family", "Difficulty": "beginner", "Question": '"நண்பர்" (naṇpar) என்ன அர்த்தம்?', "Options": ["நீங்கள் விரும்பி நேரம் கழிக்கும் நபர்", "குடும்ப உறுப்பினர்", "அறியாத நபர்", "ஆசிரியர்"], "Correct": "நீங்கள் விரும்பி நேரம் கழிக்கும் நபர்"},
    # Colors
    {"Language": "Tamil", "Category": "Colors", "Difficulty": "beginner", "Question": '"ஆப்பிளின் நிறம் என்ன?" (Āppiḷin niṟam eṉṉa?)', "Options": ["சிவப்பு அல்லது பச்சை", "நீலம்", "கருப்பு", "மஞ்சள்"], "Correct": "சிவப்பு அல்லது பச்சை"},
    {"Language": "Tamil", "Category": "Colors", "Difficulty": "beginner", "Question": '"சூரியன் எவ்வளவு நிறம்?" (Sūriyaṉ evvaḷavu niṟam?)', "Options": ["மஞ்சள்", "பச்சை", "ஊதா", "கோழை"], "Correct": "மஞ்சள்"},
    {"Language": "Tamil", "Category": "Colors", "Difficulty": "beginner", "Question": '"சிமெண்ட் நிறம் என்ன?" (Cimeṇṭ niṟam eṉṉa?)', "Options": ["பச்சை", "சிவப்பு", "வெள்ளை", "நீலம்"], "Correct": "பச்சை"},
    {"Language": "Tamil", "Category": "Colors", "Difficulty": "beginner", "Question": '"வானில் தென்றல் பகுதி என்ன நிறம்?" (Vāṉil teṉṟal pakuti eṉṉa niṟam?)', "Options": ["நீலம்", "பிங்க்", "கருப்பு", "ஆரஞ்சு"], "Correct": "நீலம்"},
    {"Language": "Tamil", "Category": "Colors", "Difficulty": "beginner", "Question": '"பனி எவ்வளவு நிறம்?" (Paṉi evvaḷavu niṟam?)', "Options": ["வெள்ளை", "சிவப்பு", "நீலம்", "மஞ்சள்"], "Correct": "வெள்ளை"},
    # Numbers
    {"Language": "Tamil", "Category": "Numbers", "Difficulty": "beginner", "Question": '"ஒன்று" (oṉṟu) என்ன அர்த்தம்?', "Options": ["1", "2", "3", "4"], "Correct": "1"},
    {"Language": "Tamil", "Category": "Numbers", "Difficulty": "beginner", "Question": '"ஐந்து" (aindu) என்ன அர்த்தம்?', "Options": ["5", "6", "7", "8"], "Correct": "5"},
    {"Language": "Tamil", "Category": "Numbers", "Difficulty": "beginner", "Question": '"பத்து" (pattu) என்ன அர்த்தம்?', "Options": ["10", "9", "11", "12"], "Correct": "10"},
    {"Language": "Tamil", "Category": "Numbers", "Difficulty": "beginner", "Question": '"மூன்று" (mūṉṟu) என்ன அர்த்தம்?', "Options": ["3", "4", "5", "6"], "Correct": "3"},
    {"Language": "Tamil", "Category": "Numbers", "Difficulty": "beginner", "Question": '"ஏழு" (ēḻu) என்ன அர்த்தம்?', "Options": ["7", "8", "9", "10"], "Correct": "7"},
    # Clothing
    {"Language": "Tamil", "Category": "Clothing", "Difficulty": "beginner", "Question": '"சமீபவாதி" (camīpavāti) என்ன அர்த்தம்?', "Options": ["உடலின் மேல் பகுதியை அணிவிக்கும் உடை", "உணவு", "காலணிகள்", "தலைக்குறிப்பு"], "Correct": "உடலின் மேல் பகுதியை அணிவிக்கும் உடை"},
    {"Language": "Tamil", "Category": "Clothing", "Difficulty": "beginner", "Question": '"காலணி" (kālaṇi) என்ன அர்த்தம்?', "Options": ["காலில் அணிவிக்கும் பொருள்", "உணவு", "உடைகள்", "துணி"], "Correct": "காலில் அணிவிக்கும் பொருள்"},
    {"Language": "Tamil", "Category": "Clothing", "Difficulty": "beginner", "Question": '"தலையணிவு" (talaiyaṇivu) என்ன அர்த்தம்?', "Options": ["தலை மீது அணியப்படும் உடை", "காலணிகள்", "உடைகள்", "பலசந்தர்ப்பு"], "Correct": "தலை மீது அணியப்படும் உடை"},
    {"Language": "Tamil", "Category": "Clothing", "Difficulty": "beginner", "Question": '"குறி" (kuṟi) என்ன அர்த்தம்?', "Options": ["உடலின் கீழ் பகுதியை அணிவிக்கும் உடை", "உணவு", "குளிர்பானம்", "தலைக்குறிப்பு"], "Correct": "உடலின் கீழ் பகுதியை அணிவிக்கும் உடை"},
    {"Language": "Tamil", "Category": "Clothing", "Difficulty": "beginner", "Question": '"முயற்சி" (muyaṟci) என்ன அர்த்தம்?', "Options": ["பெண்களால் அணிவிக்கும் உடை", "காலணிகள்", "தலையணிவு", "பலசந்தர்ப்பு"], "Correct": "பெண்களால் அணிவிக்கும் உடை"},
    # Actions
    {"Language": "Tamil", "Category": "Actions", "Difficulty": "beginner", "Question": '"வெளியே செல்ல" (veḷiyē ceṟṟa) என்ன அர்த்தம்?', "Options": ["விரைவாக நடைபயணம் செய்ய", "தூங்க", "உணவு உட்கொள்", "எழுத"], "Correct": "விரைவாக நடைபயணம் செய்ய"},
    {"Language": "Tamil", "Category": "Actions", "Difficulty": "beginner", "Question": '"உணவு உட்கொள்" (uṇavu uṭkoḷ) என்ன அர்த்தம்?', "Options": ["அன்னை பரிமாறும் உணவுக்களை உட்கொள்", "பானம் குடி", "தூங்க", "செல்ல"], "Correct": "அன்னை பரிமாறும் உணவுக்களை உட்கொள்"},
    {"Language": "Tamil", "Category": "Actions", "Difficulty": "beginner", "Question": '"பானம் குடி" (pāṉam kuṭi) என்ன அர்த்தம்?', "Options": ["பானத்தை உட்கொள்", "உணவு உட்கொள்", "தூங்க", "எழுத"], "Correct": "பானத்தை உட்கொள்"},
    {"Language": "Tamil", "Category": "Actions", "Difficulty": "beginner", "Question": '"நித்திரை எடுங்கள்" (nittirai eṭuṅkaḷ) என்ன அர்த்தம்?', "Options": ["கண் மூடி ஓய்வு எடு", "செல்ல", "உணவு உட்கொள்", "எழுதி"], "Correct": "கண் மூடி ஓய்வு எடு"},
    {"Language": "Tamil", "Category": "Actions", "Difficulty": "beginner", "Question": '"படிக்க" (paṭikka) என்ன அர்த்தம்?', "Options": ["வார்த்தைகளை பார்க்கவும் புரிந்து கொள்வதும்", "பானம் குடி", "செல்ல", "தூங்க"], "Correct": "வார்த்தைகளை பார்க்கவும் புரிந்து கொள்வதும்"},
    # Places
    {"Language": "Tamil", "Category": "Places", "Difficulty": "beginner", "Question": '"புத்தகம்" (puththakam) என்ன அர்த்தம்?', "Options": ["ஒரு இடம்", "ஒரு பெரிய தோட்டம்", "ஒரு பள்ளி", "ஒரு விடுதி"], "Correct": "ஒரு இடம்"},
    {"Language": "Tamil", "Category": "Places", "Difficulty": "beginner", "Question": '"வீடு" (vīṭu) என்ன அர்த்தம்?', "Options": ["வீட்டின் இடம்", "ஒரு அலுவலகம்", "ஒரு பள்ளி", "ஒரு விடுதி"], "Correct": "வீட்டின் இடம்"},
    {"Language": "Tamil", "Category": "Places", "Difficulty": "beginner", "Question": '"பள்ளி" (paḷḷi) என்ன அர்த்தம்?', "Options": ["கற்றல் செய்யும் இடம்", "ஒரு விடுதி", "ஒரு தொழிற்சாலை", "ஒரு வேளாண்மை நிலம்"], "Correct": "கற்றல் செய்யும் இடம்"},
    {"Language": "Tamil", "Category": "Places", "Difficulty": "beginner", "Question": '"பர்க்" (park) என்ன அர்த்தம்?', "Options": ["காட்டு விலங்குகள் மற்றும் விளையாட்டு பொருட்கள் இருக்கும் இடம்", "பள்ளி", "வாகன சேவை நிலையம்", "ரோட்டோ"], "Correct": "காட்டு விலங்குகள் மற்றும் விளையாட்டு பொருட்கள் இருக்கும் இடம்"},
    {"Language": "Tamil", "Category": "Places", "Difficulty": "beginner", "Question": '"விடுதி" (viṭudi) என்ன அர்த்தம்?', "Options": ["ஒரு தங்கும் இடம்", "கலைஞர்களுக்கான இடம்", "குளியலிடம்", "ஒரு சட்ட நிறுவன"], "Correct": "ஒரு தங்கும் இடம்"},
    # Time & Days
    {"Language": "Tamil", "Category": "Time & Days", "Difficulty": "beginner", "Question": '"காலை" (kālai) என்ன அர்த்தம்?', "Options": ["அதிகாலை நேரம்", "இரவு நேரம்", "பகல் நேரம்", "மாலை நேரம்"], "Correct": "அதிகாலை நேரம்"},
    {"Language": "Tamil", "Category": "Time & Days", "Difficulty": "beginner", "Question": '"இரவு" (iravu) என்ன அர்த்தம்?', "Options": ["இருள் நேரம்", "காலை நேரம்", "மாலை நேரம்", "பகல் நேரம்"], "Correct": "இருள் நேரம்"},
    {"Language": "Tamil", "Category": "Time & Days", "Difficulty": "beginner", "Question": '"திங்கள்" (tiṅkaḷ) என்ன அர்த்தம்?', "Options": ["வாரத்தின் முதல் நாள்", "வாரத்தின் கடைசிக் கிழமை", "மாதத்தின் முதல் நாள்", "வருடத்தின் முதல் நாள்"], "Correct": "வாரத்தின் முதல் நாள்"},
    {"Language": "Tamil", "Category": "Time & Days", "Difficulty": "beginner", "Question": '"இன்று" (iṉṟu) என்ன அர்த்தம்?', "Options": ["இன்று", "நேற்று", "நாளை", "கடந்த வாரம்"], "Correct": "இன்று"},
    {"Language": "Tamil", "Category": "Time & Days", "Difficulty": "beginner", "Question": '"வளமை" (vaḷamai) என்ன அர்த்தம்?', "Options": ["12 மாதங்கள் 365 நாட்கள்", "7 நாட்கள்", "30 நாட்கள்", "60 நிமிடங்கள்"], "Correct": "12 மாதங்கள் 365 நாட்கள்"},
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
df.to_excel('tamil_quiz_questions.xlsx', index=False) 