NEWS_CATEGORY_MAPPING = {
    # 政治類
    "政治": "政治",

    # 國際類
    "國際": "國際",

    # 兩岸類
    "兩岸": "兩岸",
    "大陸": "兩岸",

    # 財經類
    "財經": "財經",
    "產經": "財經",
    "證券": "財經",
    "理財": "財經",
    "財富自由": "財經",
    "理財房地產": "財經",

    # 科技類
    "科技": "科技",
    "3C": "科技",

    # 生活類
    "生活": "生活",

    # 社會類
    "社會": "社會",
    "公益": "社會",

    # 地方類
    "地方": "地方",

    # 文化類
    "文化": "文化",
    "藝文": "文化",

    # 運動體育類
    "運動": "運動",
    "體育": "運動",

    # 健康類
    "健康": "健康",

    # 名人娛樂類
    "娛樂": "名人娛樂",
    "影劇": "名人娛樂",

    # 交通地產類
    "汽車": "交通地產",
    "車雲": "交通地產",
    "房產": "交通地產",
    "房產雲": "交通地產",
    "地產": "交通地產",

    # 生活娛樂類
    "旅遊": "生活娛樂",
    "美食旅遊": "生活娛樂",
    "時尚": "生活娛樂",
    "寵物": "生活娛樂",
    "寵物動物": "生活娛樂",
    "女孩": "生活娛樂",
    "新奇": "生活娛樂",
    "玩咖": "生活娛樂",
    "食尚": "生活娛樂",
    "遊戲": "生活娛樂",

    # 專題
    "內幕": "專題",
}

# 確認新聞來源的類別是否都有被映射到
NEWS_SOURCES = {
    "三立新聞網": ["政治", "社會", "娛樂", "生活", "新奇", "健康", "國際", "旅遊", "運動", "兩岸", "地方", "財經", "房產", "科技", "汽車", "寵物", "女孩"],  # noqa
    "中央社": ["政治", "國際", "兩岸", "產經", "證券", "科技", "生活", "社會", "地方", "文化", "運動", "娛樂"],  # noqa
    "鏡新聞": ["政治", "國際", "財經", "社會", "生活", "娛樂", "體育", "地方", "美食旅遊", "內幕"],  # noqa
    "自由時報": ["政治", "財富自由", "社會", "生活", "健康", "國際", "地方", "財經", "娛樂", "汽車", "時尚", "體育", "3C", "藝文", "地產", "玩咖"],  # noqa
    "TVBS": ["生活", "政治", "娛樂", "國際", "社會", "健康", "體育", "理財房地產", "大陸", "汽車", "科技", "新奇", "食尚"],  # noqa
    "ettoday": ["政治", "社會", "娛樂", "影劇", "生活", "國際", "大陸", "財經", "健康", "體育", "時尚", "房產雲", "車雲", "旅遊", "寵物動物", "遊戲", "公益"]  # noqa
}
