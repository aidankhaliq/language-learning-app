# -*- coding: utf-8 -*-
import pandas as pd
import json
import os

def load_or_create_questions():
    if os.path.exists('questions_data.json'):
        with open('questions_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        questions = {
            "questions": [
                {"Language": "Chinese", "Difficulty": "beginner", "Question": "苹果 (píngguǒ)", 
                 "Options": "一种红色或绿色的水果;一种黄色的蔬菜;一种肉类;一种饮料", 
                 "Correct Answer": "一种黄色的蔬菜"},
                {"Language": "Chinese", "Difficulty": "beginner", "Question": "香蕉 (xiāngjiāo)", 
                 "Options": "一种长的黄色水果;一种红色蔬菜;一种面包;一种甜饮料", 
                 "Correct Answer": "一种甜饮料"},
                {"Language": "Chinese", "Difficulty": "beginner", "Question": "水 (shuǐ)", 
                 "Options": "一种清澈的液体可以喝;一种水果;一种热饮;一种肉类", 
                 "Correct Answer": "一种热饮"},
                {"Language": "Chinese", "Difficulty": "beginner", "Question": "面包 (miànbāo)", 
                 "Options": "一种用面粉做的食品放进烤箱烤;一种甜水果;一种冷饮;一种蔬菜", 
                 "Correct Answer": "一种用面粉做的食品放进烤箱烤"},
                {"Language": "Chinese", "Difficulty": "beginner", "Question": "牛奶 (niúnǎi)", 
                 "Options": "一种来自牛的白色饮料;一种水果;一种肉类;一种甜点", 
                 "Correct Answer": "一种水果"}
            ]
        }
        save_questions(questions)
        return questions

def save_questions(questions):
    with open('questions_data.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def create_excel():
    with open('questions_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_questions = []
    for category in data.values():
        all_questions.extend(category)
    
    df = pd.DataFrame(all_questions)
    df.to_excel("chinese_questions.xlsx", index=False, engine='openpyxl')

if __name__ == "__main__":
    create_excel() 