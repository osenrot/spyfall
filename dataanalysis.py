# Made by ***
# Comments are in Russian because I forgot to translate them in time

# Создание графиков в Plotly
import plotly
import plotly.graph_objs as go
import time
from datetime import datetime, timedelta, date
import sys
import numpy as np
import pandas as pd
sys.path.append('..')


def dates_between(first_day, last_day):
    '''Возвращает лист дат между двумя заданными датам (включительно)'''
    if isinstance(first_day, str):
        first_day = datetime.strptime(first_day, "%Y-%m-%d")
    if isinstance(last_day, str):
        last_day = datetime.strptime(last_day, "%Y-%m-%d")
    return [first_day + timedelta(days=x) for x in range(0, (last_day - first_day).days + 1)]


def plot_standard_graph(x,
                        data,
                        mode,
                        names,
                        title, x_title, y_title,
                        visible=[],
                        legend_orientation='h'):
    '''Рисует стандартный график. Из common_metrics'''
    d = []
    n = 0

    if visible == []:
        visible = [True] * len(data)

    for y in data:
        d.append(go.Scatter(x=x,
                            y=y,
                            mode=mode,
                            name=names[n],
                            visible=visible[n]))
        n += 1

    layout = go.Layout(title=title,
                       yaxis=go.YAxis(title=y_title),
                       xaxis=go.XAxis({'tickformat': '%b %d'}, title=x_title),
                       legend=dict(orientation=legend_orientation))

    fig = dict(data=d, layout=layout)
    plotly.offline.iplot(fig)


def form_cumulative_sum(data,
                        col_except_total=['cnt'],
                        total='total',
                        first_day=datetime.strptime("2018-01-01", "%Y-%m-%d"), 
                        last_day=datetime.today() - timedelta(1),
                        window=7):
    
    '''Меняет данные на кумулятивные доли 
       Вводные данные:  data - данные
                        col_except_total - названия колонок (кроме колонки суммы),
                                                   по умолчанию - одна колонка 'cnt'.
                        total - название колонки суммы, по умолчанию 'total'.
                        first_day - дата, с которой меняет, по умолчанию - "2018-01-01".
                        last_day - дата, до которой меняет, по умолчанию - вчера.
                        window - параметр сглаживания (сколько дней "окно"), по умолчанию - 7 дней.
                        
       Вывод:           датафрейм с форматированными данными 
    ''' 
    
    # Creating a counter
    line_num = 0
    
    # Data_to_graph is the list the function returns
    data_to_graph = []
    
    # Going through all the columns and changing values to ratios
    for column in col_except_total:
        
        # If the first one then start from the scratch, else accumulate values
        if line_num == 0:
            data['Доля ' + column] = data[column] / data['total']
        else:
            data['Доля ' + column] = data[column] / data['total'] + cumulative
        
        # Appending a resulting layout to the list
        # X axis - dates between the first and the last day
        # Y axis - ratio = value of the columns / total value
        data_to_graph.append(go.Scatter(x=list(map(str, dates_between(first_day, last_day))),
                                        y=data['Доля ' + column].tolist() + [None] * (365 - len(data[column].tolist())),
                                        text=round(data[column] / data['total'] * 100, 2),
                                        mode='lines', 
                                        hoverinfo='x+text',
                                        name='Доля ' + column + ' '+ str(first_day.year),
                                        fill='tonexty'
                                       )
                            )
        
        # Accumulating data
        cumulative = data['Доля ' + column]
        
        line_num += 1
        
    return data_to_graph


def plot_standard_graph(x, 
                        data, 
                        mode, 
                        names, 
                        title, x_title, y_title, 
                        visible=[], 
                        legend_orientation='h'):
    '''Рисует стандартный график.'''
    d = []
    n = 0
    
    if visible == []: 
        visible = [True]*len(data)
        
    for y in data:
        d.append(go.Scatter(x=x, 
                            y=y,
                            mode=mode, 
                            name=names[n],
                            visible=visible[n]))
        n += 1
        
    layout = go.Layout(title=title,  
                       yaxis=go.YAxis(title=y_title), 
                       xaxis=go.XAxis({'tickformat': '%b %d'}, title=x_title), 
                       legend=dict(orientation=legend_orientation))
    
    fig = dict(data=d, layout=layout)
    #plotly.offline.iplot(fig)
    plotly.io.write_image(fig, f'{title}.png')


def format_and_split_by_years(data, 
                              dt='dt', cnt='cnt',  
                              first_day=datetime.strptime("2018-01-01", "%Y-%m-%d"), 
                              last_day=datetime.today() - timedelta(1),
                              window=7
                             ):
    '''Форматирует и разбивает по годам введенные данные. Возвращает список из датафреймов.
       Вводные данные: data - датафрейм с двумя столбцами: в первом текущая дата в формате '2019-01-01', 
                                                           во втором - количество.
                       dt, cnt - названия столбцов с датами и количеством, по умолчанию - 'dt' и 'cnt'.
                       first_day - дата, с которой начинаем анализ, по умолчанию - '2018-01-01'.
                       last_day - дата, которой заканчиваем анализ, по умолчанию - вчера.
                       window - параметр сглаживания (сколько дней "окно"), по умолчанию - 7 дней.
                       
        Вывод:         лист из листов количеств по дням (количества разбиты по годам).
    '''
    
    # Меняем формат first_day и last_day в datetime, если необходимо
    if isinstance(first_day, str):
        first_day = datetime.strptime(first_day, "%Y-%m-%d")
    if isinstance(last_day, str):
        last_day = datetime.strptime(last_day, "%Y-%m-%d")
    
    # Меняем типы столбцов в датафрейме
    data[dt] = data[dt].apply(str)
#   data[cnt] = data[cnt].apply(int)

    # Сглаживаем и обрабатываем данные для каждого года
    
    # Создаем список годов между first_day и last_day
    data_to_graph = []
    years_between_list = list(range(first_day.year, last_day.year + 1))
    
    for year in years_between_list:
        
        #  Если год - не последний
        if year != last_day.year:
            m_d_this_year = [i.strftime('%m') + '-' + i.strftime('%d')\
                                 for i in dates_between(datetime(year, 1, 1), 
                                                        datetime(year, 12, 31) + timedelta(window - 1)
                                                       )
                            ]
            
            dates_year = pd.DataFrame({dt: [str(year) + '-' + m_d for m_d in m_d_this_year]})
            
        # Если год последний - срезаем данные после last_day
        # Также удаляем window последних дней, т.к. из-за сглаживания они становятся нерепрезентативными
        elif year == last_day.year:
            m_d_last_year = [i.strftime('%m') + '-' + i.strftime('%d')\
                                 for i in dates_between(datetime(year, 1, 1), 
                                                        last_day # + timedelta(window - 1)
                                                       )
                            ]
            
            dates_year = pd.DataFrame({dt: [str(year) + '-' + m_d for m_d in m_d_last_year]})
        
        # Меняем тип dt на строки
        dates_year[dt] = dates_year[dt].apply(str)
        
        # Сливаем с пустым фреймом всех дат, чтобы заполнить дни с нулевым количеством.
        data_flag = (data[dt] < str(year + 1) + '-01-01') & (data[dt] >= str(year - 1) + '-12-31')

        data_this_year = pd.merge(data[data_flag],
                                  dates_year,
                                  on=[dt],
                                  how='right'
                                 )
        
        # Заменяем NA нулями и сортируем по дате
        data_this_year = data_this_year.fillna(0).sort_values(by=dt)

        # Флаг того, что данные этого года (по циклу)
        data_to_graph_flag = (data_this_year[dt] < str(year + 1) + '-01-01') \
                             & (data_this_year[dt] >= str(year - 1) + '-12-31')
        
        # Сглаживаем, убираем NA, меняем тип на список, закидываем в итоговый список
        for column in cnt:
            # Если задано сглаживание, сглаживаем
            if window != 1:
                data_to_graph.append(data_this_year[data_to_graph_flag][column].rolling(window)\
                                                                               .mean()\
                                                                               .dropna()\
                                                                               .tolist()
                                    )
            # Иначе, не сглаживаем
            else:
                data_to_graph.append(data_this_year[data_to_graph_flag][column].dropna()\
                                                                               .tolist()
                                    )
    # Цикл 'for year in years_between_list:' останавливается здесь
    return data_to_graph


def plot_timeseries_graph(data,  
                          dt='dt', cnt='cnt',
                          first_day=datetime.strptime("2018-01-01", "%Y-%m-%d"), 
                          last_day=datetime.today() - timedelta(1),
                          window=7,
                          plot_growth=False,
                          graph_label='Продажи (шт.)',
                          growth_graph_label='Нормированный рост продаж (шт.)',
                         ):
    '''Рисует на одном рисунке несколько графиков - количество/день по годам. 
       Если указано, также рисует графики роста.
       
       Вводные данные: data - датафрейм с двумя столбцами: в первом текущая дата в формате '2019-01-01', 
                                                           во втором - количество.
                       dt, cnt - названия столбцов с датами и количеством, по умолчанию - 'dt' и 'cnt'.
                       first_day - дата, с которой начинаем анализ, по умолчанию - '2018-01-01'.
                       last_day - дата, которой заканчиваем анализ, по умолчанию - вчера.
                       window - параметр сглаживания (сколько дней "окно"), по умолчанию - 7 дней.
                       plot_growth - флаг, надо ли строить график роста, по умолчанию - False.
                       graph_label - название графика, по умолчанию - 'Продажи (шт.)'.
                       growth_graph_label - название графика роста, 
                                            по умолчанию - 'Нормированный рост продаж (шт.)'.
                       
        Вывод:         нет.
    '''
    
    # Меняем формат first_day и last_day в datetime, если необходимо
    if isinstance(first_day, str):
        first_day = datetime.strptime(first_day, "%Y-%m-%d")
    if isinstance(last_day, str):
        last_day = datetime.strptime(last_day, "%Y-%m-%d")
        
    # Создаем список годов между first_day и last_day
    years_between_list = list(range(first_day.year, last_day.year + 1))
    
    # Создаем список подписей для графиков из годов и названий колонок
    column_names_by_years = []
    for year in years_between_list:
        for column in cnt:
            column_names_by_years.append(str(column) + '_' + str(year))
        
    # Форматируем и разбиваем данные по годам    
    data_to_graph = format_and_split_by_years(data, dt, cnt, first_day, last_day, window)

    # Рисуем графики количество/день по годам
    plot_standard_graph(list(map(str, dates_between(first_day, last_day))),
                        data_to_graph,
                        'lines', 
                        column_names_by_years,
                        graph_label,
                        "", 
                        graph_label
                        )
    
    # Если plot_growth, рисуем графики роста
    if plot_growth:
        
        # Ставим датой начала продукта первый день с ненулевым количеством
        product_start_day = data[data[cnt] > 0].iloc[0][dt]
       
        # Меняем тип даты начала продукта на строку
        if isinstance(product_start_day, str):
            product_start_day = datetime.strptime(product_start_day, "%Y-%m-%d")
        
        # Удаляем первые нули для изменения формы данных (доля от первого ненулевого количества)
        # Затем обратно добавляем первые нули
        data_to_graph[0] = data_to_graph[0][(product_start_day - first_day).days:]
        data_growth = list(map(lambda x: form_grow(x), data_to_graph))
        data_growth[0] = [0] * (product_start_day - first_day).days + data_growth[0]
        
        
        # Рисуем графики роста
        plot_standard_graph(list(map(str, dates_between(first_day, last_day))),
                            data_growth, 
                            'lines', 
                            column_names_by_years,
                            growth_graph_label,
                            "", 
                            "рост от изначального значения в году, %"
                            )


def plot_cumulative_sum_graph(data,  
                              dt='dt', columns=['cnt'],
                              first_day=datetime.strptime("2018-01-01", "%Y-%m-%d"), 
                              last_day=datetime.today() - timedelta(1),
                              window=7,
                              graph_names='Структура продаж, '
                             ):
    '''Рисует на одном рисунке несколько графиков - пропорции по указанным колонкам по годам. 
       Если указано, также рисует графики роста.
       
       Вводные данные: data - датафрейм с двумя столбцами: в первом текущая дата в формате '2019-01-01', 
                                                           во втором - количество.
                       dt - название столбца с датами, по умолчанию - 'dt'.
                       columns - названия столбцов с остальными данными, по умолчанию - ['cnt']
                       first_day - дата, с которой начинаем анализ, по умолчанию - '2018-01-01'.
                       last_day - дата, которой заканчиваем анализ, по умолчанию - вчера.
                       window - параметр сглаживания (сколько дней "окно"), по умолчанию - 7 дней.
                       
        Вывод:         нет.
     '''
    
    # Меняем формат first_day и last_day в datetime, если необходимо
    if isinstance(first_day, str):
        first_day = datetime.strptime(first_day, "%Y-%m-%d")
    if isinstance(last_day, str):
        last_day = datetime.strptime(last_day, "%Y-%m-%d")
        
    # Форматируем и разбиваем данные по годам
    data_dict = {}
    for column in columns:
        data_dict[column] = format_and_split_by_years(data[[dt, column]],
                                                      dt=dt,
                                                      cnt=[column],
                                                      first_day=first_day,
                                                      last_day=last_day,
                                                      window=window
                                                      )
    
    # Создаем список годов между first_day и last_day
    years_between_list = list(range(first_day.year, last_day.year + 1))
    
    # Рисуем графики за каждый год
    i = 0
    for year in years_between_list:
        
        temp_dict = {}
        
        # Извлекам данные для текущего года из словарей столбцов
        for column in columns:
            temp_dict[column] = data_dict[column][i]
        data_to_graph = pd.DataFrame(temp_dict)
        
        # Меняем форму данных на кумулятивные суммы по столбцам
        data_to_graph = form_cumulative_sum(data_to_graph,
                                            first_day=first_day,
                                            last_day=last_day,
                                            col_except_total=[item for item in columns if item != 'total'],
                                            window=window
                                           )
        
        # Рисуем графики в pyplot
        layout = go.Layout(title=graph_names + str(year), 
                           xaxis=go.XAxis({'tickformat': '%b %d'}), 
                           yaxis=go.YAxis({'tickformat': ',.2%'}), 
                           legend=dict(orientation="h")
                           )
    
        fig = dict(data=data_to_graph, 
                   layout=layout
                   )

        #plotly.offline.iplot(fig)
        plotly.io.write_image(fig, f'{title}.png')
        i += 1
