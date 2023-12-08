import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re
import streamlit as st

#plt.style.use('seaborn')

@st.cache_data
def read_files():
    sales_alm = pd.read_excel('Продажи АЛМ.xlsx')
    sales_ast = pd.read_excel('Продажи АСТ.xlsx')
    sales_smt = pd.read_excel('Продажи ШМТ.xlsx')

    stocks_alm = pd.read_excel('Остатки АЛМ.xlsx')
    stocks_ast = pd.read_excel('Остатки АСТ.xlsx')
    stocks_smt = pd.read_excel('Остатки ШМТ.xlsx')

    stats_alm = pd.read_excel('Стат параметры АЛМ.xlsx')
    stats_ast = pd.read_excel('Стат параметры АСТ.xlsx')
    stats_smt = pd.read_excel('Стат параметры ШМТ.xlsx')
    
    sales_alm.index = sales_alm['ДАТА']
    sales_ast.index = sales_ast['ДАТА']
    sales_smt.index = sales_smt['ДАТА']

    stocks_alm.index = stocks_alm['ДАТА']
    stocks_ast.index = stocks_ast['ДАТА']
    stocks_smt.index = stocks_smt['ДАТА']
    
    suppliers = pd.read_excel('data\ПАРАМЕТРЫ ПОСТАВЩИКОВ.xlsx')

    suppliers['ПОСТАВЩИК'] = suppliers['ПОСТАВЩИК'].apply(lambda x: x[:15])
    
    return sales_alm, sales_ast, sales_smt, stocks_alm, stocks_ast, stocks_smt, stats_alm, stats_ast, stats_smt, suppliers


sales_alm, sales_ast, sales_smt, stocks_alm, stocks_ast, stocks_smt, stats_alm, stats_ast, stats_smt, suppliers = read_files()

#Напишем заголовок                
st.title("Визуализация динамики продаж по артикулу на 3х складах")                


art =   st.number_input(
        label="Введите артикул с точностью до дубликата по названию",
        value=120100
    )  

art = int(art)



sales = [sales_alm, sales_ast, sales_smt]
stocks = [stocks_alm, stocks_ast, stocks_smt]
stats = [stats_alm, stats_ast, stats_smt]

for i in range(3):
    stats[i] = stats[i].fillna({'ДУБЛИКАТЫ':""})

art_set = set()

for i in range(3):
    if stats[i][stats[i]['АРТИКУЛ'] == art].shape[0]>0:
        art_name = stats[i][stats[i]['АРТИКУЛ'] == art]['ТОВАР'].iloc[0]

for i in range(3):
    if stats[i][stats[i]['ТОВАР'] == art_name]['АРТИКУЛ'].shape[0]>0:
        art_main = stats[i][stats[i]['ТОВАР'] == art_name]['АРТИКУЛ'].iloc[0]
        dubs = stats[i][stats[i]['ТОВАР'] == art_name]['ДУБЛИКАТЫ'].iloc[0]
        art_set = art_set.union({str(art_main)})
        if len(dubs) > 0:
            art_set = art_set.union(set(re.sub(r'[,\[\]]','',dubs).split()))


art_list = list()
for x in art_set:
    art_list.append(int(x))
    


d = {0:'АЛМ', 1: 'АСТ', 2: 'ШМТ'}


for art in art_list:
    for i in range(3):

        regularity_days = 10
        transport_days = 8
        
        if stats[i][stats[i]['АРТИКУЛ'] == art].shape[0]>0:
            supplier = stats[i][stats[i]['АРТИКУЛ'] == art]['ПОСТАВЩИК'].iloc[0]
    
            if supplier in list(suppliers['ПОСТАВЩИК'].values):
                regularity_days = suppliers[suppliers['ПОСТАВЩИК']== supplier]['РЕГУЛЯРНОСТЬ ДНИ'].iloc[0]
                transport_days = suppliers[suppliers['ПОСТАВЩИК']== supplier]['ПЛЕЧО ДНИ'].iloc[0] 
        
        if stats[i][stats[i]['АРТИКУЛ'] == art].shape[0]>0:
            s = '\n' + d[i] + '\n'
            art_name = stats[i][stats[i]['АРТИКУЛ'] == art]['ТОВАР'].iloc[0]
            curr_stock = stats[i][stats[i]['АРТИКУЛ'] == art]['curr_stock'].iloc[0]
            deficit_level = stats[i][stats[i]['АРТИКУЛ'] == art]['deficit_level'].iloc[0]
            risk_zone_level = stats[i][stats[i]['АРТИКУЛ'] == art]['risk_zone_level'].iloc[0]
            optimum_zone_level = stats[i][stats[i]['АРТИКУЛ'] == art]['optimum_zone_level'].iloc[0]
            overstock_level = stats[i][stats[i]['АРТИКУЛ'] == art]['overstock_level'].iloc[0]
            mean_level = stats[i][stats[i]['АРТИКУЛ'] == art]['sales_mean'].iloc[0]
            sales_dynamics = stats[i][stats[i]['АРТИКУЛ'] == art]['sales_sym'].iloc[0]
            s += 'Кластер: ' + stats[i][stats[i]['АРТИКУЛ']==art]['cluster_name'].iloc[0]+ '\n'
            s += 'Регулярность дни: ' + str(regularity_days)+ '\n'
            s += 'Плечо дни: ' + str(transport_days) + '\n'

            stock_on_income = max([curr_stock - mean_level*transport_days,0])
            s += 'Остаток к приходу: ' + str(stock_on_income) + '\n'
            s += 'Середина оптимального остатка: ' + str((optimum_zone_level + (overstock_level-optimum_zone_level)/2).round(0))+ '\n'
            s += 'Cредние продажи в день: ' + str(mean_level.round(0)) + '\n'

            aim_stock = (risk_zone_level + mean_level*regularity_days)*(1+sales_dynamics)
            s += 'Целевой остаток: ' + str(aim_stock.round(0)) + '\n'
            order = stats[i][stats[i]['АРТИКУЛ'] == art]['order'].iloc[0]
            s += 'Заказ: '+ str(order.round(0)) + '\n'
            s += 'Дубликаты: ' + str(art_list) + '\n'
            s += 'КЛИЕНТОВ: ' + str(stats[i][stats[i]['АРТИКУЛ']==art]['КЛИЕНТОВ'].iloc[0])+ '\n'
            s += 'Динамика продаж: ' + str(stats[i][stats[i]['АРТИКУЛ'] == art]['sales_sym'].iloc[0].round(2))


            fig, ax = plt.subplots(1,1, figsize = [8,3])
            sns.lineplot(stocks[i][art].T, ax=ax)

            if art in list(sales[i].columns):
                sns.lineplot(sales[i][art].T, ax=ax)
            line = pd.DataFrame(stocks[i][art].T.copy())

            if art in list(sales[i].columns):
                std_level = (mean_level + 3*sales[i].describe().T.loc[art]['std'])
            else:
                std_level = 0

            line['mean'] = mean_level
            line['deficit'] = deficit_level
            line['overstock_level'] = stats[i][stats[i]['АРТИКУЛ']== art]['overstock_level'].iloc[0]
            line['aim'] = aim_stock
            line['risk'] = risk_zone_level
            line['opt'] = optimum_zone_level
            ax.set_title(d[i] +' '+art_name)

            sns.lineplot(line, ax=ax)
            
            st.write(fig)
            st.text(s)