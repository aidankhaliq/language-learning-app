import pandas as pd
import random

# Define the quiz questions data (with correct answer always first for now)
questions_data = [
    # Food & Drinks
    {"Language": "Chinese", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": '"苹果" (píngguǒ) 在中文是什么意思？', "Options": ["一种红色或绿色的水果", "一种黄色的蔬菜", "一种肉类", "一种饮料"], "Correct": "一种红色或绿色的水果"},
    {"Language": "Chinese", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": '"香蕉" (xiāngjiāo) 是什么意思？', "Options": ["一种长的黄色水果", "一种红色蔬菜", "一种面包", "一种甜饮料"], "Correct": "一种长的黄色水果"},
    {"Language": "Chinese", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": '"水" (shuǐ) 在中文中是什么意思？', "Options": ["一种清澈的液体，可以喝", "一种水果", "一种热饮", "一种肉类"], "Correct": "一种清澈的液体，可以喝"},
    {"Language": "Chinese", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": '"面包" (miànbāo) 是什么意思？', "Options": ["一种用面粉做的食品，放进烤箱烤", "一种甜水果", "一种冷饮", "一种蔬菜"], "Correct": "一种用面粉做的食品，放进烤箱烤"},
    {"Language": "Chinese", "Category": "Food & Drinks", "Difficulty": "beginner", "Question": '"牛奶" (niúnǎi) 在中文中是什么意思？', "Options": ["一种来自牛的白色饮料", "一种水果", "一种肉类", "一种甜点"], "Correct": "一种来自牛的白色饮料"},
    # Animals
    {"Language": "Chinese", "Category": "Animals", "Difficulty": "beginner", "Question": '"狗" (gǒu) 是什么意思？', "Options": ["一种常见的宠物，喜欢吠叫", "一只大猫", "一只会飞的鸟", "一种海洋中的鱼"], "Correct": "一种常见的宠物，喜欢吠叫"},
    {"Language": "Chinese", "Category": "Animals", "Difficulty": "beginner", "Question": '"猫" (māo) 是什么意思？', "Options": ['一种小动物，叫声是"喵"', "一只大动物，咆哮", "一只会唱歌的鸟", "一种鱼"], "Correct": '一种小动物，叫声是"喵"'},
    {"Language": "Chinese", "Category": "Animals", "Difficulty": "beginner", "Question": '"鸟" (niǎo) 是什么意思？', "Options": ["一种有翅膀的动物，可以飞翔", "一种会游泳的大动物", "一种小昆虫", "一种鱼"], "Correct": "一种有翅膀的动物，可以飞翔"},
    {"Language": "Chinese", "Category": "Animals", "Difficulty": "beginner", "Question": '"鱼" (yú) 在中文中是什么意思？', "Options": ["一种生活在水里的动物", "一种大型陆生动物", "一种飞行动物", "一种昆虫"], "Correct": "一种生活在水里的动物"},
    {"Language": "Chinese", "Category": "Animals", "Difficulty": "beginner", "Question": '"马" (mǎ) 是什么意思？', "Options": ["一种用来骑的大家伙", "一只小宠物像猫", "一种飞鸟", "一种水生动物"], "Correct": "一种用来骑的大家伙"},
    # Objects
    {"Language": "Chinese", "Category": "Objects", "Difficulty": "beginner", "Question": '"书" (shū) 是什么意思？', "Options": ["用来阅读的物品", "一种食物", "一种饮料", "一种鞋子"], "Correct": "用来阅读的物品"},
    {"Language": "Chinese", "Category": "Objects", "Difficulty": "beginner", "Question": '"笔" (bǐ) 在中文中是什么意思？', "Options": ["用来写字的工具", "一种食物", "一种衣服", "一种座位"], "Correct": "用来写字的工具"},
    {"Language": "Chinese", "Category": "Objects", "Difficulty": "beginner", "Question": '"椅子" (yǐzi) 是什么意思？', "Options": ["用来坐的家具", "一种食物", "用来写字的工具", "一种包包"], "Correct": "用来坐的家具"},
    {"Language": "Chinese", "Category": "Objects", "Difficulty": "beginner", "Question": '"包" (bāo) 在中文中是什么意思？', "Options": ["用来装东西的容器", "一种食物", "一种饮料", "一个睡觉的地方"], "Correct": "用来装东西的容器"},
    {"Language": "Chinese", "Category": "Objects", "Difficulty": "beginner", "Question": '"钥匙" (yuèshi) 是什么意思？', "Options": ["一种用来开锁的小工具", "一种水果", "一种饮料", "一种衣服"], "Correct": "一种用来开锁的小工具"},
    # Family
    {"Language": "Chinese", "Category": "Family", "Difficulty": "beginner", "Question": '"妈妈" (māmā) 是什么意思？', "Options": ["女性父母", "男性父母", "兄弟", "朋友"], "Correct": "女性父母"},
    {"Language": "Chinese", "Category": "Family", "Difficulty": "beginner", "Question": '"爸爸" (bàba) 是什么意思？', "Options": ["男性父母", "女性父母", "姐妹", "老师"], "Correct": "男性父母"},
    {"Language": "Chinese", "Category": "Family", "Difficulty": "beginner", "Question": '"兄弟" (xiōngdì) 在中文中是什么意思？', "Options": ["男性兄妹", "女性兄妹", "父母", "朋友"], "Correct": "男性兄妹"},
    {"Language": "Chinese", "Category": "Family", "Difficulty": "beginner", "Question": '"姐妹" (jiěmèi) 是什么意思？', "Options": ["女性兄妹", "男性兄妹", "父母", "老师"], "Correct": "女性兄妹"},
    {"Language": "Chinese", "Category": "Family", "Difficulty": "beginner", "Question": '"朋友" (péngyǒu) 是什么意思？', "Options": ["你喜欢并一起度过时光的人", "家庭成员", "陌生人", "老师"], "Correct": "你喜欢并一起度过时光的人"},
    # Colors
    {"Language": "Chinese", "Category": "Colors", "Difficulty": "beginner", "Question": "苹果的颜色是什么？", "Options": ["红色或绿色", "蓝色", "黑色", "黄色"], "Correct": "红色或绿色"},
    {"Language": "Chinese", "Category": "Colors", "Difficulty": "beginner", "Question": "太阳的颜色是什么？", "Options": ["黄色", "绿色", "紫色", "棕色"], "Correct": "黄色"},
    {"Language": "Chinese", "Category": "Colors", "Difficulty": "beginner", "Question": "草地的颜色是什么？", "Options": ["绿色", "红色", "白色", "蓝色"], "Correct": "绿色"},
    {"Language": "Chinese", "Category": "Colors", "Difficulty": "beginner", "Question": "晴天的天空是什么颜色？", "Options": ["蓝色", "粉红色", "黑色", "橙色"], "Correct": "蓝色"},
    {"Language": "Chinese", "Category": "Colors", "Difficulty": "beginner", "Question": "雪的颜色是什么？", "Options": ["白色", "红色", "蓝色", "黄色"], "Correct": "白色"},
    # Numbers
    {"Language": "Chinese", "Category": "Numbers", "Difficulty": "beginner", "Question": '"一" (yī) 是什么意思？', "Options": ["1", "2", "3", "4"], "Correct": "1"},
    {"Language": "Chinese", "Category": "Numbers", "Difficulty": "beginner", "Question": '"五" (wǔ) 是什么意思？', "Options": ["5", "6", "7", "8"], "Correct": "5"},
    {"Language": "Chinese", "Category": "Numbers", "Difficulty": "beginner", "Question": '"十" (shí) 是什么意思？', "Options": ["10", "9", "11", "12"], "Correct": "10"},
    {"Language": "Chinese", "Category": "Numbers", "Difficulty": "beginner", "Question": '"三" (sān) 是什么意思？', "Options": ["3", "4", "5", "6"], "Correct": "3"},
    {"Language": "Chinese", "Category": "Numbers", "Difficulty": "beginner", "Question": '"七" (qī) 是什么意思？', "Options": ["7", "8", "9", "10"], "Correct": "7"},
    # Clothing
    {"Language": "Chinese", "Category": "Clothing", "Difficulty": "beginner", "Question": '"衬衫" (chènshān) 是什么意思？', "Options": ["上身的衣服", "食物", "鞋子", "帽子"], "Correct": "上身的衣服"},
    {"Language": "Chinese", "Category": "Clothing", "Difficulty": "beginner", "Question": '"鞋子" (xiézi) 是什么意思？', "Options": ["穿在脚上的物品", "食物", "饮料", "包包"], "Correct": "穿在脚上的物品"},
    {"Language": "Chinese", "Category": "Clothing", "Difficulty": "beginner", "Question": '"帽子" (màozi) 是什么意思？', "Options": ["戴在头上的物品", "下面的衣服", "鞋子", "包包"], "Correct": "戴在头上的物品"},
    {"Language": "Chinese", "Category": "Clothing", "Difficulty": "beginner", "Question": '"裤子" (kùzi) 在中文中是什么意思？', "Options": ["穿在腿上的衣服", "食物", "饮料", "帽子"], "Correct": "穿在腿上的衣服"},
    {"Language": "Chinese", "Category": "Clothing", "Difficulty": "beginner", "Question": '"裙子" (qúnzi) 是什么意思？', "Options": ["穿在女性身上的衣服", "鞋子", "帽子", "包包"], "Correct": "穿在女性身上的衣服"},
    # Actions
    {"Language": "Chinese", "Category": "Actions", "Difficulty": "beginner", "Question": '"跑" (pǎo) 是什么意思？', "Options": ["快速地跑步", "睡觉", "吃", "写字"], "Correct": "快速地跑步"},
    {"Language": "Chinese", "Category": "Actions", "Difficulty": "beginner", "Question": '"吃" (chī) 是什么意思？', "Options": ["把食物放进嘴巴里并吞咽", "喝", "睡觉", "跑步"], "Correct": "把食物放进嘴巴里并吞咽"},
    {"Language": "Chinese", "Category": "Actions", "Difficulty": "beginner", "Question": '"喝" (hē) 在中文中是什么意思？', "Options": ["喝液体", "吃", "睡觉", "写字"], "Correct": "喝液体"},
    {"Language": "Chinese", "Category": "Actions", "Difficulty": "beginner", "Question": '"睡觉" (shuìjiào) 是什么意思？', "Options": ["闭上眼睛并休息", "跑步", "吃", "读书"], "Correct": "闭上眼睛并休息"},
    {"Language": "Chinese", "Category": "Actions", "Difficulty": "beginner", "Question": '"读书" (dúshū) 是什么意思？', "Options": ["看书并理解", "喝", "跑步", "睡觉"], "Correct": "看书并理解"},
    # Places
    {"Language": "Chinese", "Category": "Places", "Difficulty": "beginner", "Question": '"学校" (xuéxiào) 是什么意思？', "Options": ["学生学习的地方", "食物", "睡觉的地方", "游泳的地方"], "Correct": "学生学习的地方"},
    {"Language": "Chinese", "Category": "Places", "Difficulty": "beginner", "Question": '"家" (jiā) 在中文中是什么意思？', "Options": ["人们居住的地方", "学校", "公园", "餐馆"], "Correct": "人们居住的地方"},
    {"Language": "Chinese", "Category": "Places", "Difficulty": "beginner", "Question": '"公园" (gōngyuán) 是什么意思？', "Options": ["有草地、树木和游乐场的地方", "学校", "医院", "商店"], "Correct": "有草地、树木和游乐场的地方"},
    {"Language": "Chinese", "Category": "Places", "Difficulty": "beginner", "Question": '"医院" (yīyuàn) 是什么意思？', "Options": ["病人接受治疗的地方", "学校", "餐馆", "公园"], "Correct": "病人接受治疗的地方"},
    {"Language": "Chinese", "Category": "Places", "Difficulty": "beginner", "Question": '"餐馆" (cānguǎn) 是什么意思？', "Options": ["吃饭的地方", "学校", "医院", "公园"], "Correct": "吃饭的地方"},
    # Time & Days
    {"Language": "Chinese", "Category": "Time & Days", "Difficulty": "beginner", "Question": '"早上" (zǎoshang) 在中文是什么意思？', "Options": ["一天的开始时间 (清晨)", "晚上的时间", "中午的时间", "下午的时间"], "Correct": "一天的开始时间 (清晨)"},
    {"Language": "Chinese", "Category": "Time & Days", "Difficulty": "beginner", "Question": '"晚上" (wǎnshàng) 是什么意思？', "Options": ["一天中天黑后到睡觉时间的时段", "早上的时间", "中午的时间", "下午的时间"], "Correct": "一天中天黑后到睡觉时间的时段"},
    {"Language": "Chinese", "Category": "Time & Days", "Difficulty": "beginner", "Question": '"星期一" (xīngqī yī) 是什么意思？', "Options": ["一周的第一天", "一周的最后一天", "一个月的第一天", "一个季节的第一天"], "Correct": "一周的第一天"},
    {"Language": "Chinese", "Category": "Time & Days", "Difficulty": "beginner", "Question": '"今天" (jīntiān) 是什么意思？', "Options": ["当前的一天", "昨天", "明天", "下个星期"], "Correct": "当前的一天"},
    {"Language": "Chinese", "Category": "Time & Days", "Difficulty": "beginner", "Question": '"年" (nián) 在中文中是什么意思？', "Options": ["12个月，365天", "一天", "一个月", "一星期"], "Correct": "12个月，365天"}
]

# Shuffle correct answer position for each question
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

# Create DataFrame
df = pd.DataFrame(questions_data)

# Save to Excel
df.to_excel('chinese_quiz_questions.xlsx', index=False)
print("Excel file 'chinese_quiz_questions.xlsx' has been created successfully with 50 questions.") 