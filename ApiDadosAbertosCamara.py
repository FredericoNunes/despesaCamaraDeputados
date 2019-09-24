import requests
from pandas.io.json import json_normalize
import re
from sqlalchemy import create_engine

url = "https://dadosabertos.camara.leg.br/api/v2/deputados"
headers = {
    'Cache-Control': "no-cache",
    'Postman-Token': "6a245b59-ae14-6ba4-886b-cf29f2c1496c",
    'accept':  "application/json"
    }
tabela_dados_basicos = []
tabela_dados_basicos_completa = []
tabela_despesas = []
lista_id = []

for legislatura in range (50,57):
    for pagina_deputados in range (1,8):
        querystring = {"idLegislatura":str(legislatura),"pagina":str(pagina_deputados),"itens":"100"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        tabela_dados_basicos.append(response.json())
        print(legislatura)

df = json_normalize(tabela_dados_basicos,'dados')

for i, id_deputados in enumerate(df[df.idLegislatura==53].iterrows()):
    id_deputado_camara = id_deputados[1]["id"]
    id_legislatura = id_deputados[1]["idLegislatura"]
    url = f'https://dadosabertos.camara.leg.br/api/v2/deputados/{id_deputado_camara}/despesas'
    querystring = {"idLegislatura":str(id_legislatura),"itens":"100"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    lastpagejson = response.json()["links"]
    ultimapagina_re = re.search( 'idLegislatura={}&pagina=(.*)&itens=100'.format(str(id_legislatura)),
                                  lastpagejson[-1]['href'])
    try:
        ultimapagina = int(ultimapagina_re.group(1))
    except:
        ultimapagina = 1 # remover
    for pagina_despesas in range(1, ultimapagina+1):
        querystring = {"idLegislatura": str(id_legislatura), "pagina": str(pagina_despesas), "itens": "100"}
        pagina_despesas_response = requests.request("GET", url, headers=headers, params=querystring)
        resposta = pagina_despesas_response.json()["dados"]
        print({"legislatura": id_legislatura,
               "paginaDespesas":pagina_despesas,
               "id_depudado":id_deputado_camara,
               "paginas":ultimapagina})
        if resposta:
            for i , x in enumerate(resposta):
                resposta[0]["id_deputado_camara"] = id_deputado_camara
                try:
                    valorliquido = float(resposta[0]["valorLiquido"])
                except:
                    valorliquido = 0
                resposta[0]["valorLiquido"] = valorliquido
        tab = {"dados": resposta}
        df_despesas = json_normalize(tab,'dados')