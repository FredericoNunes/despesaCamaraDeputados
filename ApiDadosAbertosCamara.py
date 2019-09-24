import requests
from pandas.io.json import json_normalize
import re


class ApiDadosAbertosCamara:
    def __init__(self):
        self.URL = "https://dadosabertos.camara.leg.br/api/v2/deputados"
        self.HEADERS = {
            'Cache-Control': "no-cache",
            'Postman-Token': "6a245b59-ae14-6ba4-886b-cf29f2c1496c",
            'accept':  "application/json"
        }


    def get_deputados_por_legislatura(self,**kwargs):
        tabela_dados_basicos = []
        for pagina_deputados in range (1,8):
            querystring = {"idLegislatura":str(kwargs.get('legislatura')),
                           "pagina":str(pagina_deputados),
                           "itens":"100"}
            response = requests.request("GET",
                                        self.URL,
                                        headers=self.HEADERS,
                                        params=querystring)
            tabela_dados_basicos.append(response.json())

        return json_normalize(tabela_dados_basicos,'dados')

    def get_depesas_por_deputado_e_legislatura(self,**kwargs):
        df = self.get_deputados_por_legislatura(legislatura=kwargs.get('legislatura'))
        tabela_despesas = []
        for i, id_deputados in enumerate(df[df.idLegislatura==53].iterrows()):
            id_deputado_camara = id_deputados[1]["id"]
            id_legislatura = id_deputados[1]["idLegislatura"]
            url = f'https://dadosabertos.camara.leg.br/api/v2/deputados/{id_deputado_camara}/despesas'
            querystring = {"idLegislatura":str(id_legislatura),"itens":"100"}
            response = requests.request("GET",
                                        self.URL,
                                        headers=self.HEADERS,
                                        params=querystring)
            lastpagejson = response.json()["links"]
            ultimapagina_re = re.search( 'idLegislatura={}&pagina=(.*)&itens=100'.format(str(id_legislatura)),
                                          lastpagejson[-1]['href'])
            try:
                ultimapagina = int(ultimapagina_re.group(1))
            except:
                ultimapagina = 1 # remover
            for pagina_despesas in range(1, ultimapagina+1):
                querystring = {"idLegislatura": str(id_legislatura), "pagina": str(pagina_despesas), "itens": "100"}
                pagina_despesas_response = requests.request("GET", url, headers=self.HEADERS, params=querystring)
                resposta = pagina_despesas_response.json()["dados"]
                print({"legislatura": id_legislatura,
                       "paginaDespesas":pagina_despesas,
                       "id_depudado":id_deputado_camara,
                       "paginas":ultimapagina})

                tabela_despesas.append({"dados": resposta})
        return json_normalize(tabela_despesas,'dados')

