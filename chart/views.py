from django.shortcuts import render
from .models import Passenger
from django.db.models import Count, Q
import json
import pandas as pd
from django.http import JsonResponse    #for chart_data()
from .models import Covid

def home(request):
    return render(request, 'home.html')


def world_population(request):
    return render(request, 'world_population.html')

def ju_covid_19(request):
    return render(request, 'jupyterlab_covid_19.html')

def covid_19(request):

    df = pd.read_csv('https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv',
                     parse_dates=['Date'])

    # 분석 대상 국가에 해당하는 행 선별
    countries = ['France', 'Germany', 'Korea, South', 'US', 'United Kingdom']
    df = df[df['Country'].isin(countries)]
    # 합계 열 생성
    df['Cases'] = df[['Confirmed', 'Recovered', 'Deaths']].sum(axis=1)
    #데이터 재구조화
    df = df.pivot(index='Date', columns='Country',values='Cases')
    countries = list(df.columns)
    #기존 인덱스 열을 데이터 열로 변경
    covid = df.reset_index('Date')
    #covid 인덱스와 columns를 새로 지정
    covid.set_index(['Date'], inplace=True)
    covid.columns = countries

    populations = {'France': 65273511, 'Germany': 83783942, 'Korea, South': 51269185, 'US': 331002651, 'United Kingdom': 67886011}
    percapita = covid.copy()
    for country in list(percapita.columns):
        percapita[country] = percapita[country] / populations[country] * 1000000

    percapita.to_csv("covid19.csv", header=True, index=True)

    dataset = Covid.objects.values()

    #빈 리스트 준비
    categories = list()
    date_series = list()
    france_series = list()
    germany_series = list()
    korea_series = list()
    us_series = list()
    uk_series = list()

    # 리스트 3종에 형식화된 값 등록
    for entry in dataset:
        categories.append(entry['date'])
        france_series.append(entry['france']),
        germany_series.append(entry['germany']),
        korea_series.append(entry['korea']),
        us_series.append(entry['us']),
        uk_series.append(entry['uk'])

    date = list()  # 빈 리스트 준비
    for i in categories:
        date.append(i.strftime('%e. %b'))

    # json.dumps() 함수로 리스트 3종을 JSON 데이터 형식으로 반환
    return render(request, 'covid_19.html', {
        'date': json.dumps(date_series),
        'france_series': json.dumps(france_series),
        'germany_series': json.dumps(germany_series),
        'korea_series': json.dumps(korea_series),
        'us_series': json.dumps(us_series),
        'uk_series': json.dumps(uk_series)
    })

def ticket_class_view_1(request):  # 방법 1
    dataset = Passenger.objects \
        .values('ticket_class') \
        .annotate(
            survived_count=Count('ticket_class',
                                 filter=Q(survived=True)),
            not_survived_count=Count('ticket_class',
                                     filter=Q(survived=False))) \
        .order_by('ticket_class')
    return render(request, 'ticket_class_1.html', {'dataset': dataset})
#  dataset = [
#    {'ticket_class': 1, 'survived_count': 200, 'not_survived_count': 123},
#    {'ticket_class': 2, 'survived_count': 119, 'not_survived_count': 158},
#    {'ticket_class': 3, 'survived_count': 181, 'not_survived_count': 528}
#  ]



def ticket_class_view_2(request):  # 방법 2
    dataset = Passenger.objects \
        .values('ticket_class') \
        .annotate(survived_count=Count('ticket_class', filter=Q(survived=True)),
                  not_survived_count=Count('ticket_class', filter=Q(survived=False))) \
        .order_by('ticket_class')

    # 빈 리스트 3종 준비
    categories = list()             # for xAxis
    survived_series = list()        # for series named 'Survived'
    not_survived_series = list()    # for series named 'Not survived'
    survival_rate = list()

    # 리스트 3종에 형식화된 값을 등록
    for entry in dataset:
        categories.append('%s Class' % entry['ticket_class'])    # for xAxis
        survived_series.append(entry['survived_count'])          # for series named 'Survived'
        not_survived_series.append(entry['not_survived_count'])  # for series named 'Not survived'
        survival_rate.append(entry['survived_count']/(entry['survived_count']+entry['not_survived_count'])*100)

    # json.dumps() 함수로 리스트 3종을 JSON 데이터 형식으로 반환
    return render(request, 'ticket_class_2.html', {
        'categories': json.dumps(categories),
        'survived_series': json.dumps(survived_series),
        'not_survived_series': json.dumps(not_survived_series),
        'survival_rate': json.dumps(survival_rate)
    })


def ticket_class_view_3(request):  # 방법 3
    dataset = Passenger.objects \
        .values('ticket_class') \
        .annotate(survived_count=Count('ticket_class', filter=Q(survived=True)),
                  not_survived_count=Count('ticket_class', filter=Q(survived=False))) \
        .order_by('ticket_class')

    # 빈 리스트 3종 준비 (series 이름 뒤에 '_data' 추가)
    categories = list()                 # for xAxis
    survived_series_data = list()       # for series named 'Survived'
    not_survived_series_data = list()   # for series named 'Not survived'

    # 리스트 3종에 형식화된 값을 등록
    for entry in dataset:
        categories.append('%s Class' % entry['ticket_class'])         # for xAxis
        survived_series_data.append(entry['survived_count'])          # for series named 'Survived'
        not_survived_series_data.append(entry['not_survived_count'])  # for series named 'Not survived'

    survived_series = {
        'name': 'Survived',
        'data': survived_series_data,
        'color': 'green'
    }
    not_survived_series = {
        'name': 'Survived',
        'data': not_survived_series_data,
        'color': 'red'
    }

    chart = {
        'chart': {'type': 'column'},
        'title': {'text': 'Titanic Survivors by Ticket Class'},
        'xAxis': {'categories': categories},
        'series': [survived_series, not_survived_series]
    }
    dump = json.dumps(chart)

    return render(request, 'ticket_class_3.html', {'chart': dump})


def json_example(request):  # 접속 경로 'json-example/'에 대응하는 뷰
    return render(request, 'json_example.html')


def chart_data(request):  # 접속 경로 'json-example/data/'에 대응하는 뷰
    dataset = Passenger.objects \
        .values('embarked') \
        .exclude(embarked='') \
        .annotate(total=Count('id')) \
        .order_by('-total')
    #  [
    #    {'embarked': 'S', 'total': 914}
    #    {'embarked': 'C', 'total': 270},
    #    {'embarked': 'Q', 'total': 123},
    #  ]

    # # 탑승_항구 상수 정의
    # CHERBOURG = 'C'
    # QUEENSTOWN = 'Q'
    # SOUTHAMPTON = 'S'
    # PORT_CHOICES = (
    #     (CHERBOURG, 'Cherbourg'),
    #     (QUEENSTOWN, 'Queenstown'),
    #     (SOUTHAMPTON, 'Southampton'),
    # )
    port_display_name = dict()
    for port_tuple in Passenger.PORT_CHOICES:
        port_display_name[port_tuple[0]] = port_tuple[1]
    # port_display_name = {'C': 'Cherbourg', 'Q': 'Queenstown', 'S': 'Southampton'}

    chart = {
        'chart': {'type': 'pie'},
        'title': {'text': 'Number of Titanic Passengers by Embarkation Port'},
        'series': [{
            'name': 'Embarkation Port',
            'data': list(map(
                lambda row: {'name': port_display_name[row['embarked']], 'y': row['total']},
                dataset))
            # 'data': [ {'name': 'Southampton', 'y': 914},
            #           {'name': 'Cherbourg', 'y': 270},
            #           {'name': 'Queenstown', 'y': 123}]
        }]
    }
    # [list(map(lambda))](https://wikidocs.net/64)

    return JsonResponse(chart)

