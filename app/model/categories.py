coco_categories = [
{ "id": 1, "name": "livingroom", "supercategory": "" },
{ "id": 2, "name": "bedroom", "supercategory": "" },
{ "id": 3, "name": "kitchen", "supercategory": "" },
{ "id": 4, "name": "bathroom", "supercategory": "" },
{ "id": 5, "name": "closet", "supercategory": "" },
{ "id": 6, "name": "generic_room", "supercategory": "" },
{ "id": 7, "name": "balcony_terrace", "supercategory": "" },
{ "id": 8, "name": "diningroom", "supercategory": "" },
{ "id": 9, "name": "foyer_hall", "supercategory": "" }
]

categories = list(map((lambda cat: cat['name'].replace('_',' ').capitalize()), coco_categories))
