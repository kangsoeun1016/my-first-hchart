#chart/migrations/0004_auto_popuate.py
"""
DB 현행화 작업이 실행될 때, csv 파일 자료를 DB에 자동적으로 적재한다.
"""
import csv
import os
import datetime
from django.db import migrations
from django.conf import settings

def add_covid(apps, schema_editor):
    Covid = apps.get_model('chart', 'Covid')  # (app_label, model_name)
    csv_file = os.path.join(settings.BASE_DIR, 'covid19.csv')
    with open(csv_file) as dataset:                   # 파일 객체 dataset
        reader = csv.reader(dataset)                    # 파일 객체 dataset에 대한 판독기 획득
        next(reader)  # ignore first row (headers)      # __next__() 호출 때마다 한 라인 판독
        for entry in reader:                            # 판독기에 대하여 반복 처리
            Covid.objects.create(                       # DB 행 생성
                date=datetime.datetime.strptime(entry[0], '%Y-%m-%d'),
                france=float(entry[1]),
                germany=float(entry[2]),
                korea=float(entry[3]),
                us=float(entry[4]),
                uk=float(entry[5]),
            )

class Migration(migrations.Migration):
    dependencies = [                            # 선행 관계
        ('chart', '0003_covid'),         # app_label, preceding migration file
    ]
    operations = [                              # 작업
        migrations.RunPython(add_covid),   # add_passengers 함수를 호출
    ]