# create_dataset.py
import pandas as pd
import os

# Your data
data = """Plant,Stage,Temperature,Humidity,Light,Age,N,P,K
Tomato,Seedling,24,70,6000,10,90,40,60
Tomato,Vegetative,26,65,9000,25,180,60,200
Tomato,Flowering,27,60,11000,40,200,70,260
Tomato,Fruiting,28,58,12000,60,190,65,300
Cucumber,Seedling,23,75,5500,8,80,35,55
Cucumber,Vegetative,25,70,8500,20,160,55,180
Cucumber,Flowering,26,65,10000,35,180,65,240
Cucumber,Fruiting,27,60,11000,55,170,60,270
Lettuce,Seedling,21,80,4500,6,60,25,45
Lettuce,Vegetative,23,75,7500,15,120,40,140
Lettuce,Harvest,24,70,8500,28,110,35,160
Spinach,Seedling,22,75,5000,7,70,30,50
Spinach,Vegetative,24,70,8000,18,140,50,150
Spinach,Harvest,25,65,9000,30,130,45,170
Sprouts,Early,20,85,3000,3,40,20,30
Sprouts,Mid,22,80,4000,5,60,30,50
Sprouts,Ready,24,75,5000,7,80,40,70
Chilli,Seedling,24,70,6500,9,85,35,55
Chilli,Vegetative,26,65,9000,22,170,60,200
Chilli,Flowering,27,60,10500,38,190,65,250
Chilli,Fruiting,28,58,11500,58,180,60,290
Capsicum,Seedling,24,72,6000,10,85,38,58
Capsicum,Vegetative,26,66,9000,25,175,58,195
Capsicum,Fruiting,28,60,11500,60,185,62,285
Beans,Seedling,23,74,5500,9,75,32,52
Beans,Vegetative,25,70,8200,20,150,52,170
Beans,Flowering,26,65,9800,35,165,60,230
Peas,Seedling,22,76,5200,8,70,30,48
Peas,Vegetative,24,71,8000,18,140,48,160
Peas,Flowering,25,66,9500,32,155,55,210
Coriander,Seedling,21,80,4800,7,55,22,40
Coriander,Vegetative,23,75,7800,16,115,38,130
Coriander,Harvest,24,70,8200,28,105,34,150
Mint,Seedling,22,78,5000,8,60,25,45
Mint,Vegetative,24,73,8000,20,130,45,150
Mint,Harvest,25,70,8800,32,120,40,165
Onion,Seedling,22,77,5200,9,65,28,48
Onion,Bulbing,25,68,9000,40,150,55,190
Garlic,Seedling,21,78,5000,10,60,26,46
Garlic,Bulbing,25,68,9000,45,145,52,185
Radish,Seedling,22,76,5100,8,70,30,50
Radish,Rooting,24,70,8200,25,135,45,165
Broccoli,Seedling,20,75,5000,8,70,30,50
Broccoli,Vegetative,23,70,8000,20,140,50,160
Broccoli,Harvest,25,65,9000,35,130,45,180
Cauliflower,Seedling,20,78,4800,7,65,28,48
Cauliflower,Vegetative,24,70,8200,22,150,55,170
Cauliflower,Harvest,26,65,9000,40,140,50,190
Cabbage,Seedling,21,80,4500,8,60,25,45
Cabbage,Vegetative,24,72,8000,20,135,45,160
Cabbage,Harvest,26,68,9000,45,125,40,180
Okra,Seedling,24,70,6000,9,80,35,55
Okra,Vegetative,27,65,9000,25,170,60,190
Okra,Fruiting,29,60,11500,55,180,65,260
Eggplant,Seedling,24,70,6000,10,85,35,60
Eggplant,Vegetative,26,65,9000,25,175,60,200
Eggplant,Fruiting,28,60,11500,60,185,65,280
Strawberry,Seedling,20,75,5000,7,60,25,45
Strawberry,Vegetative,22,70,8000,18,120,40,150
Strawberry,Fruiting,24,65,9000,40,110,35,180
Basil,Seedling,22,75,4800,6,55,22,40
Basil,Vegetative,25,70,8000,20,120,40,150
Basil,Harvest,26,65,8500,30,110,35,160
Parsley,Seeding,21,78,4600,7,50,20,38
Parsley,Vegetative,23,72,7800,18,110,35,140
Parsley,Harvest,25,68,8500,32,100,30,155
Celery,Seedling,20,80,4500,8,60,25,45
Celery,Vegetative,23,75,7800,22,130,45,160
Celery,Harvest,25,70,8800,45,120,40,180
Kale,Seedling,21,78,4800,7,65,28,48
Kale,Vegetative,24,72,8200,20,140,50,165
Kale,Harvest,26,68,9000,40,130,45,185
Arugula,Seedling,20,80,4500,6,55,22,40
Arugula,Vegetative,22,75,7500,15,115,38,145
Arugula,Harvest,24,70,8200,28,105,34,160
Fenugreek,Seedling,22,78,4700,6,50,20,38
Fenugreek,Vegetative,24,72,7800,16,110,35,140
Fenugreek,Harvest,25,68,8500,25,100,30,155
MustardGreens,Seedling,21,80,4600,6,55,22,40
MustardGreens,Vegetative,23,75,7800,15,120,40,150
MustardGreens,Harvest,25,70,8500,28,110,35,165
Zucchini,Seedling,23,72,5500,9,80,35,55
Zucchini,Vegetative,26,65,9000,25,170,60,190
Zucchini,Fruiting,28,60,11500,55,180,65,260
Watermelon,Seedling,24,70,6000,10,85,35,60
Watermelon,Vegetative,27,65,9500,30,180,65,210
Watermelon,Fruiting,30,60,12000,65,190,70,300
Beetroot,Seedling,22,75,5200,8,70,30,50
Beetroot,Vegetative,24,70,8000,20,140,50,160
Beetroot,Rooting,25,65,8800,35,130,45,180
Turnip,Seedling,21,78,5000,7,65,28,48
Turnip,Vegetative,23,72,7800,18,130,45,155
Turnip,Rooting,24,68,8500,32,120,40,170
SwissChard,Seedling,22,78,4800,7,60,25,45
SwissChard,Vegetative,24,72,8200,20,140,50,165
SwissChard,Harvest,26,68,9000,40,130,45,185
PakChoi,Seedling,21,80,4500,6,55,22,40
PakChoi,Vegetative,23,75,7800,15,120,40,150
PakChoi,Harvest,25,70,8500,28,110,35,165
IcebergLettuce,Seedling,20,82,4300,6,55,22,40
IcebergLettuce,Vegetative,22,76,7600,15,115,38,145
IcebergLettuce,Harvest,24,72,8300,30,105,34,160
RomaineLettuce,Seedling,21,80,4500,6,60,25,45
RomaineLettuce,Vegetative,23,75,7800,16,120,40,150
RomaineLettuce,Harvest,25,70,8500,28,110,35,165
CherryTomato,Seedling,24,70,6000,10,90,40,60
CherryTomato,Vegetative,26,65,9000,25,175,60,200
CherryTomato,Fruiting,28,58,11500,60,185,65,290
Cilantro,Seedling,21,80,4800,7,55,22,40
Cilantro,Vegetative,23,75,7800,16,115,38,130
Cilantro,Harvest,24,70,8200,28,105,34,150
Dill,Seedling,22,78,5000,7,60,25,45
Dill,Vegetative,24,72,8000,18,125,42,150
Dill,Harvest,25,68,8500,30,115,38,165
Thyme,Seedling,22,75,4800,8,55,22,40
Thyme,Vegetative,25,70,7800,22,120,40,150
Thyme,Harvest,26,65,8500,35,110,35,160
Oregano,Seedling,22,75,4800,8,55,22,40
Oregano,Vegetative,25,70,8000,22,120,40,150
Oregano,Harvest,26,65,8500,35,110,35,160
Rosemary,Seedling,22,72,5000,9,60,25,45
Rosemary,Vegetative,25,68,8200,25,130,45,160
Rosemary,Harvest,27,65,8800,45,120,40,170
Endive,Seedling,20,80,4500,6,55,22,40
Endive,Vegetative,22,75,7500,15,115,38,145
Endive,Harvest,24,70,8200,28,105,34,160
Leek,Seedling,22,78,5000,8,65,28,48
Leek,Vegetative,24,72,8000,22,135,45,160
Leek,Bulbing,26,68,8800,45,145,52,185
Asparagus,Seedling,22,75,5200,10,70,30,50
Asparagus,Vegetative,25,70,8200,30,150,55,180
Asparagus,Harvest,27,65,9000,60,140,50,200
BokChoy,Seedling,21,80,4500,6,55,22,40
BokChoy,Vegetative,23,75,7800,15,120,40,150
BokChoy,Harvest,25,70,8500,28,110,35,165
CollardGreens,Seedling,22,78,4800,7,60,25,45
CollardGreens,Vegetative,24,72,8200,20,140,50,165
CollardGreens,Harvest,26,68,9000,40,130,45,185
Sorrel,Seedling,21,80,4600,6,55,22,40
Sorrel,Vegetative,23,75,7800,15,115,38,145
Sorrel,Harvest,25,70,8500,28,105,34,160
Chives,Seedling,22,78,5000,7,60,25,45
Chives,Vegetative,24,72,8000,18,125,42,150
Chives,Harvest,26,68,8800,35,115,38,165
Fennel,Seedling,22,75,5000,8,65,28,48
Fennel,Vegetative,25,70,8200,22,140,50,165
Fennel,Harvest,27,65,9000,45,130,45,185
Kohlrabi,Seedling,21,78,4800,7,60,25,45
Kohlrabi,Vegetative,24,72,8000,20,135,45,160
Kohlrabi,Harvest,26,68,8800,40,125,40,180
Radicchio,Seedling,20,80,4500,6,55,22,40
Radicchio,Vegetative,22,75,7600,15,115,38,145
Radicchio,Harvest,24,70,8200,30,105,34,160
MalabarSpinach,Seedling,24,75,5500,8,70,30,50
MalabarSpinach,Vegetative,27,70,9000,25,150,55,170
MalabarSpinach,Harvest,29,65,10000,45,140,50,185
Watercress,Seedling,20,82,4300,6,55,22,40
Watercress,Vegetative,22,78,7600,15,120,40,150
Watercress,Harvest,24,72,8300,28,110,35,165
Tatsoi,Seedling,21,80,4500,6,55,22,40
Tatsoi,Vegetative,23,75,7800,15,120,40,150
Tatsoi,Harvest,25,70,8500,28,110,35,165
SummerSquash,Seedling,24,70,6000,10,85,35,60
SummerSquash,Vegetative,27,65,9000,25,175,60,200
SummerSquash,Fruiting,29,60,11500,55,185,65,280
Pumpkin,Seedling,24,70,6000,10,85,35,60
Pumpkin,Vegetative,27,65,9500,30,180,65,210
Pumpkin,Fruiting,30,60,12000,65,190,70,300
Palak,Seedling,22,78,5000,7,70,30,50
Palak,Vegetative,24,72,8000,18,140,50,150
Palak,Harvest,25,68,8800,30,130,45,170
Methi,Seedling,22,78,4700,6,50,20,38
Methi,Vegetative,24,72,7800,16,110,35,140
Methi,Harvest,25,68,8500,25,100,30,155
Amaranthus,Seedling,23,76,5200,7,65,28,48
Amaranthus,Vegetative,26,70,8500,20,150,55,170
Amaranthus,Harvest,28,65,9200,35,140,50,185
DrumstickLeaves,Seedling,24,75,5500,8,70,30,50
DrumstickLeaves,Vegetative,27,70,9000,25,155,55,180
DrumstickLeaves,Harvest,29,65,10000,45,145,50,190
CurryLeaves,Seedling,24,72,5500,9,65,28,48
CurryLeaves,Vegetative,27,68,9000,25,140,50,165
CurryLeaves,Harvest,29,65,9800,40,130,45,180
BottleGourd,Seedling,24,70,6000,10,85,35,60
BottleGourd,Vegetative,27,65,9500,30,175,60,200
BottleGourd,Fruiting,30,60,12000,65,185,65,280
RidgeGourd,Seedling,24,70,6000,10,85,35,60
RidgeGourd,Vegetative,27,65,9500,30,175,60,200
RidgeGourd,Fruiting,30,60,12000,65,185,65,280
SnakeGourd,Seedling,24,70,6000,10,85,35,60
SnakeGourd,Vegetative,27,65,9500,30,175,60,200
SnakeGourd,Fruiting,30,60,12000,65,185,65,280
BitterGourd,Seedling,24,70,6000,10,85,35,60
BitterGourd,Vegetative,27,65,9500,30,175,60,200
BitterGourd,Fruiting,30,60,12000,65,185,65,280
ClusterBeans,Seedling,23,74,5500,9,75,32,52
ClusterBeans,Vegetative,25,70,8200,20,150,52,170
ClusterBeans,Harvest,27,65,9000,35,140,48,185
Cowpea,Seedling,23,75,5500,9,75,32,52
Cowpea,Vegetative,25,70,8200,20,150,52,170
Cowpea,Harvest,27,65,9000,35,140,48,185
IndianMustard,Seedling,22,78,4800,6,55,22,40
IndianMustard,Vegetative,24,72,8000,16,120,40,150
IndianMustard,Harvest,25,68,8500,28,110,35,165
Tinda,Seedling,24,70,6000,10,85,35,60
Tinda,Vegetative,27,65,9500,30,175,60,200
Tinda,Fruiting,30,60,12000,65,185,65,280"""

# Parse the data
from io import StringIO
df = pd.read_csv(StringIO(data))

# Rename columns
df.columns = ["plant", "stage", "temperature", "humidity", "light_lux", "age_days", "N", "P", "K"]

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Save with UTF-8 encoding
df.to_csv("data/hydro_data.csv", index=False, encoding='utf-8')

print(f"✅ Created data/hydro_data.csv with {len(df)} rows")
print(f"✅ Columns: {', '.join(df.columns)}")
print(f"\n📊 Sample data:")
print(df.head())