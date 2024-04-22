
from natasha import NamesExtractor

from yargy import Parser, rule, and_, not_, or_
from yargy.interpretation import fact
from yargy.predicates import gram, gte, lte, eq, type, dictionary
from yargy.relations import gnc_relation
from yargy.pipelines import morph_pipeline
from yargy.tokenizer import MorphTokenizer
from yargy.interpretation import fact
from IPython.display import display


#sents = open('msc.txt').read().splitlines()
sents = open('vvs.txt', "r", encoding="utf-8").read().splitlines()
for i in sents:
    print(i)

gnc = gnc_relation()


Name = fact(
    'Name',
    ['first', 'last']
)

Person = fact(
    'Person',
    ['occupation', 'belongs', 'name']
)


Aircraft = fact(
    'Aircraft',
    ['description', 'aircaft_class', 'aircaft_model']
)

Aircraft_cl = fact(
    'Aircraft_cl',
    ['class_of_air']
)

Date = fact(
    'Date',
    ['year', 'month', 'day']
)

Period = fact(
    'Period',
    ['start_year', 'end_year']
)

Country = fact(
    'Country',
    ['name_of_country']
)


Design_department = fact(
    'Design_department',
    ['dd', 'name_of_department']
)


OCCUPATION = morph_pipeline([               #Должности сотрудников КБ и участников испытаний
    'председатель',
    'командарм',
    'генерал-лейтенант'
    'начальник',
    'заместитель начальника',
    'лётчик-ас',
    'лётчик',
    'Маршал Советского Союза ',
    'командующий',
    'летчики-истрибители',
    'генерал-майор',
    'лётчик-испытатель',
    'маршал'
])


AIRCRAFT_CLASS = morph_pipeline([               #Класс самолетов
    'разведчик',
    'бомбардировщик',
    'истребитель',
    'биплан',
    'штурмовик',
    'самолёт-истребитель',
    'истребитель-бомбардировщик',
    'фронтовой истребитель',
    'палубный штурмовик',
    'истребитель-перехватчик',
])

AIRCRAFT_LETTER = morph_pipeline([               #Названия самолетов
    'Р',
    'СБ',
    'ДБ',
    'И',
    'ТБ',
    'He',
    'Bf',
    'МиГ',
    'Як',
    'ЛаГГ',
    'Пе',
    'Ла',
    'Ил',
    'Ту',
    'P',
    'A',
    'PBY',
    'C'
    'Хоукер Харрикейн',
    'Супермарин Спитфайр',
    'Me',
    'He',
    '«Метеор»',
    '«Вампир»',
    '«Веном»',
    'F',
    'MD',
    '«Мистер»',
    '«Хантер»',
    'B',
    'Су',
    'F/A',
    '«Торнадо»',
    '«Мираж»',
    'СУ'
])

AIRCRAFT_ADDITIONAL_NAME = morph_pipeline([               #Класс самолетов
    'Хейнкель',
    'Мессершмитт',
    'Чайка'
])

MONTHS = {          #Месяцы
    'январь',
    'февраль',
    'март',
    'апрель',
    'мая',
    'июнь',
    'июль',
    'август',
    'сентябрь',
    'октябрь',
    'ноябрь',
    'декабрь'
}


COUNTRIES = morph_pipeline([               #Страны
    'СССР',
    'США',
    'Россия'
    'Литва',
    'Латвия',
    'Эстония',
    'Испания',
    'Китай',
    'Финляндия',
    'Монголия',
    'Япония',
    'Великобритания',
    'Советский Союз',
    'Германия',
    'КНДР',
    'Северная Корея',
    'Корея',
    'Афганистан'
])

DD = morph_pipeline([ 
    'КБ',
    'ОКБ',
    'конструкторское бюро'
])


NAME = or_(                                 #Помогает выделить имя (инициалы выделяются через ИМЯ. ИМЯ. Фамилия или ИМЯ. Фамилия, т.к. грамматики Отчество найти не получилось)
    rule(
        gram('Name').interpretation(
            Name.first.inflected()
        ),
        '.',
        gram('Name'),
        '.',
        gram('Surn').interpretation(
            Name.last.inflected()
        ).match(gnc)
    ),
    rule(
        gram('Name').interpretation(
            Name.first.inflected()
        ),
        '.',
        gram('Surn').interpretation(
            Name.last.inflected()
        ).match(gnc)
    ),
    rule(
        gram('Name').interpretation(
            Name.first.inflected()
        ),
        gram('Surn').interpretation(
            Name.last.inflected()
        )
    ),
    rule(
        gram('Surn').interpretation(
            Name.last.inflected()
        )
    ),  
    rule(
        gram('Name').interpretation(
            Name.first.inflected()
        )
    ) 
).interpretation(
    Name
) 



PERSON = or_(                             # Описание сотрудника/участника
    rule(
        OCCUPATION.interpretation(
            Person.occupation.inflected()
        ).match(gnc),
        and_(
            not_(eq(OCCUPATION)),
            not_(eq(NAME)),
            not_(eq('.'))
        ).repeatable().interpretation(
            Person.belongs.inflected()
        ),
        NAME.interpretation(
            Person.name
        ).match(gnc)
    ),
    rule(
        OCCUPATION.interpretation(
            Person.occupation.inflected()
        ),
        NAME.interpretation(
            Person.name
        )
    )
).interpretation(
    Person
)


NUMBER_OF_MODEL = type('INT')   #Число для номера модели самолетов

MODEL_NAME = or_(    # Выделение полного названия самолета, например Як-9 или Bf.109
    rule(
        AIRCRAFT_LETTER,
        '-',
        NUMBER_OF_MODEL
    ),
    rule(
        AIRCRAFT_LETTER,
        '.',
        NUMBER_OF_MODEL
    ),
    rule(
        AIRCRAFT_ADDITIONAL_NAME,
        AIRCRAFT_LETTER,
        '.',
        NUMBER_OF_MODEL
    ),
    rule(
        AIRCRAFT_LETTER,
        '.',
        NUMBER_OF_MODEL,
        AIRCRAFT_ADDITIONAL_NAME
    ),
)


AIRCRAFT = or_(         # Выделение класса самолета с типом (например реактивный), если такие имеются + полного названия самолета с помощью правила MODEL_NAME
    rule(
        AIRCRAFT_CLASS.interpretation(
            Aircraft.aircaft_class.inflected()
        ).match(gnc),
        MODEL_NAME.interpretation(
            Aircraft.aircaft_model
        )
    ),
    rule(
        gram('ADJF').interpretation(
            Aircraft.description.inflected()
        ).match(gnc),
        AIRCRAFT_CLASS.interpretation(
            Aircraft.aircaft_class.inflected()
        ).match(gnc),
        MODEL_NAME.interpretation(
            Aircraft.aircaft_model
        )
    ),
    rule(
        MODEL_NAME.interpretation(
            Aircraft.aircaft_model
        ) 
    )
).interpretation(
    Aircraft
)

AIRCRAFT_CL = or_(          #Тетсовый варинато для проверки (не используется)
        rule(
        AIRCRAFT_CLASS.interpretation(
            Aircraft_cl.class_of_air.inflected()
        ),
    ),
)


MONTH_NAME = dictionary(MONTHS)     

MONTH = and_(       #Выделение месяца, ввиде числа 
    gte(1),
    lte(12)
)
DAY = and_(     #Выделение дня
    gte(1),
    lte(31)
)
YEAR = and_(    #Выделение года
    gte(1900),
    lte(2100)
)


DATE = or_(     #Выделение полной даты, состоящец из числа, месяца и года и отдельно года (в тексте часто указываетсяч отдельно год и всё)
    rule(
        DAY.interpretation(
            Date.day
        ),
        MONTH_NAME.interpretation(
            Date.month
        ),
        YEAR.interpretation(
            Date.year
        )
    ),
    rule(
        YEAR.interpretation(
            Date.year
        ),
        'год'
    )
).interpretation(
    Date
)

PERIOD = or_(        #Выделение периода времени вида: 1900-1950, 1900-1950-х, с 1900 по 1950
    rule(
        YEAR.interpretation(
            Period.start_year
        ),
        '-',
        YEAR.interpretation(
            Period.end_year
        )
    ),
    rule(
        YEAR.interpretation(
            Period.start_year
        ),
        '-',
        YEAR.interpretation(
            Period.end_year
        ),
        '-х'
    ),
    rule(
        'с',
        YEAR.interpretation(
            Period.start_year
        ),
        'по',
        YEAR.interpretation(
            Period.end_year
        )
    )
).interpretation(
    Period
)

COUNTRY = rule(         #Выделение стран в тексте
    COUNTRIES.interpretation(
        Country.name_of_country.inflected()
    )
).interpretation(
    Country
)

DESIGN_DEPARTMENT = rule(       #Выделение конструкторских бюро (КБ/ОКБ/конструкторское бюро + фамилия основателя)
    DD.interpretation(
        Design_department.dd.inflected()
    ),
    gram('Surn').interpretation(
        Design_department.name_of_department.inflected()
    ).match(gnc)
).interpretation(
    Design_department
)

Proxy = fact('Proxy', ['value'])        # Сущность, чтобы отображать сразу все остальные
#EMPLOYEE, AIRCRAFT, DATE, PERIOD, COUNTRY
ALL = or_(PERSON, AIRCRAFT, DATE, PERIOD, COUNTRY, DESIGN_DEPARTMENT).interpretation(Proxy.value).interpretation(Proxy)

parser = Parser(ALL)


for sent in sents:
    for match in parser.findall(sent):
        display(match.fact)
    print('---')

matches = []

for sent in sents:
    for match in parser.findall(sent):
        matches.append(match.fact)

final_file = open("final_file.txt", "w", encoding="utf-8")
for mtch in matches:
    final_file.write(str(mtch))
    final_file.write('\n')

final_file.close()
