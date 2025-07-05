import json
import os
import random
import re

from ..mcp.cliente import MCPCliente
from ..utils.util import quebra_linha
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


genai.configure(api_key=GEMINI_API_KEY)
modelo = genai.GenerativeModel('gemini-1.5-flash')

class AgenteVirtual:
    def __init__(self, config_path="config/veiculos.json"):
        self.cliente = MCPCliente()
        with open(config_path, 'r', encoding='utf-8') as arquivo:
            config = json.load(arquivo)
        self.marcas_modelos = config.get('marcas_modelos', {})
        self.combustiveis_validos = ['Gasolina', 'Diesel', 'Etanol', 'Flex', 'Híbrido', 'Elétrico', 'GNV']
        self.opcionais = config.get('opcionais', [])
        self.filtros = {}
        self.perguntas = [
            ("Qual a marca de carro você está procurando?", self.consultar_marca),
            ("Tem algum modelo específico em mente ou quer sugestões?", self.consultar_modelo),
            ("Qual o ano do veículo que seria ideal para você?", self.consultar_ano),
            ("Qual a faixa de preço que você está pensando? (ex.: de 50.000 a 100.000)", self.consultar_preco),
            ("O carro precisa ter ar condicionado ou isso não é prioridade?", self.consultar_arCondicionado),
            ("Tem algum item opcional que você faz questão? (teto solar, multimídia, airbag...)",
             self.consultar_opcionais),
            ("Você prefere carros novos, seminovos ou tanto faz?", self.consultar_condicao),
            ("Prefere câmbio manual ou automático?", self.consultar_transmissao),
            ("Tem alguma cor de carro que você gostaria de evitar?", self.consultar_cor),
            ("Tem preferência por combustível? Gasolina, diesel, flex ou elétrico?", self.consultar_combustivel),
            ("Tem um limite de quilometragem para o carro usado?", self.consultar_quilometragem),
        ]

    def gemini(self, input_text):
        with open('config/veiculos.json', 'r', encoding='utf-8') as arquivo:
            config = json.load(arquivo)
        opcionais_validos = config.get('opcionais', [])

        prompt = f"""
            Você é um assistente especializado em carros que entende linguagem natural.
            O usuário irá descrever o carro ideal para ele, podendo usar termos específicos (ex.: marca, modelo) ou genéricos (ex.: "espaçoso", "grande").
            Extraia filtros no formato JSON com as seguintes chaves possíveis:
            - marca
            - modelo
            - ano
            - preco_min
            - preco_max
            - ar_condicionado (true/false)
            - opcionais (lista de strings, apenas de: {opcionais_validos})
            - condicao (Novo, Seminovo, Usado)
            - transmissao (Manual, Automático)
            - cor_evitar
            - combustivel
            - quilometragem_max
            - portas

            Marcas disponíveis: {list(self.marcas_modelos.keys())}
            Opcionais válidos: {opcionais_validos}

            Regras adicionais:
            - Para termos como "espaçoso" ou "grande", interprete como veículos com 5 portas (ex.: SUVs, minivans) e sugira marcas/modelos como "Jeep Compass", "Honda HR-V", "Toyota Corolla Cross".
            - Não adicione opcionais que não estejam na lista de opcionais válidos.
            - Se não identificar filtros específicos, retorne um JSON com filtros genéricos (ex.: portas=5, marca="Jeep", modelo="Compass").
            - Sempre retorne um JSON válido, mesmo que seja vazio ({{}}).

            Exemplo de resposta para "carro grande":
            {{
                "portas": 5,
                "marca": "Jeep",
                "modelo": "Compass"
            }}

            IMPORTANTE: Responda APENAS com JSON válido, sem texto adicional.

            Usuário: "{input_text}"
        """
        try:
            resposta = modelo.generate_content(prompt)
            texto = resposta.text.strip()
            #DEBUG:
            #print(f"resp gemini: {texto}")

            # VALIDA ALGUNS TRECHOS DA RESPOSTA DO GEMINI
            if texto.startswith('```json'):
                texto = texto[7:]

            if texto.endswith('```'):
                texto = texto[:-3]

            texto = texto.strip()

            if '{' in texto and '}' in texto:
                inicio = texto.find('{')
                fim = texto.rfind('}') + 1
                texto = texto[inicio:fim]

            # Debug:
            # print(f"Texto JSON retornado: {texto}")

            filtros_extraidos = json.loads(texto)

            # Debug:
            # print(f"Filtros retornados do Gemini: {filtros_extraidos}")

            filtros_validados = self._validar_filtros(filtros_extraidos)
            return filtros_validados



        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON do Gemini: {e}")
            print(f"Texto recebido: {texto}")
            return self._extrair_filtros_manual(input_text)


        except Exception as e:
            print(f"Erro ao processar resposta do Gemini: {e}")
            return self._extrair_filtros_manual(input_text)


    def _validar_filtros(self, filtros):
        filtros_validados = {}
        with open('config/veiculos.json', 'r', encoding='utf-8') as arquivo:
            config = json.load(arquivo)
        opcionais_validos = config.get('opcionais', [])


        if 'marca' in filtros:
            marca = filtros['marca']
            # TENTA ENCONTRAR UMA MARCA PARECIDA
            if marca in self.marcas_modelos:
                filtros_validados['marca'] = marca
            else:
                for marca_valida in self.marcas_modelos.keys():
                    if marca.lower() in marca_valida.lower() or marca_valida.lower() in marca.lower():
                        filtros_validados['marca'] = marca_valida
                        break


        if 'modelo' in filtros and 'marca' in filtros_validados:
            modelo = filtros['modelo']
            modelos_marca = self.marcas_modelos[filtros_validados['marca']]
            if modelo in modelos_marca:
                filtros_validados['modelo'] = modelo
            else:

                # Aqui eu tento encontrar algum modelo parecido
                for modelo_valido in modelos_marca:
                    if modelo.lower() in modelo_valido.lower() or modelo_valido.lower() in modelo.lower():
                        filtros_validados['modelo'] = modelo_valido
                        break


        if 'opcionais' in filtros:
            filtros_validados['opcionais'] = [opc for opc in filtros['opcionais'] if opc in opcionais_validos]


        if 'portas' in filtros and filtros['portas'] in [2, 4, 5]:
            filtros_validados['portas'] = filtros['portas']

        for chave in ['ano', 'preco_min', 'preco_max', 'ar_condicionado', 'condicao',
                      'transmissao', 'cor_evitar', 'combustivel', 'quilometragem_max', 'portas']:
            if chave in filtros:
                filtros_validados[chave] = filtros[chave]

        #print(f"Filtros validados: {filtros_validados}")
        return filtros_validados



    def _extrair_filtros_manual(self, input_text):

        filtros = {}
        texto_lower = input_text.lower()

        for marca in self.marcas_modelos.keys():
            if marca.lower() in texto_lower:
                filtros['marca'] = marca
                break

        if 'marca' in filtros:
            for modelo in self.marcas_modelos[filtros['marca']]:
                if modelo.lower() in texto_lower:
                    filtros['modelo'] = modelo
                    break

        anos = re.findall(r'\b(20\d{2})\b', texto_lower)
        if anos:
            filtros['ano'] = int(anos[0])

        # EXTRAI COMBUSTIVEL
        for comb in self.combustiveis_validos:
            if comb.lower() in texto_lower:
                filtros['combustivel'] = comb
                break

        # REGEX: captura a parte inteira de um valor decimal opcional e sufixo abreviado
        numeros = re.findall(r'(\d+)(?:\.\d+)?(?:k|mil|000)?', texto_lower)
        if numeros:
            preco = int(numeros[0]) * 1000 if len(numeros[0]) <= 3 else int(numeros[0])
            filtros['preco_max'] = preco

        return filtros



    def atualizar_filtros(self, novos_filtros):

        for chave, valor in novos_filtros.items():
            if valor is not None and valor != '':
                self.filtros[chave] = valor
                # print(f"Filtro atualizado: {chave} = {valor}")




    def consultar_marca(self, resposta):
        if resposta.lower() in ['qualquer', 'tanto faz', 'nenhuma']:
            return True

        for marca in self.marcas_modelos.keys():
            if marca.lower() == resposta.lower():
                self.filtros['marca'] = marca
                return True


        for marca in self.marcas_modelos.keys():
            if resposta.lower() in marca.lower() or marca.lower() in resposta.lower():
                print(f"Você quis dizer {marca}? (s/n)")
                confirmacao = input().lower()
                if confirmacao in ['s', 'sim', 'y', 'yes']:
                    self.filtros['marca'] = marca
                    return True



        marcas_disponiveis = ', '.join(self.marcas_modelos.keys())
        print(f"Marca não encontrada. Marcas disponíveis: {marcas_disponiveis}")
        return False

    def consultar_modelo(self, resposta):

        if resposta.lower() in ['quero sugestão', 'sugestão', 'sugira', 'qualquer', 'sugestao', 'tanto faz']:
            if 'marca' in self.filtros and self.filtros['marca'] in self.marcas_modelos:
                modelos = self.marcas_modelos[self.filtros['marca']]
                modelo_sugerido = random.choice(modelos)
                print(f"Que tal um {self.filtros['marca']} {modelo_sugerido}?")
                self.filtros['modelo'] = modelo_sugerido
                return True
            else:
                print("Por favor, informe uma marca antes de pedir sugestões de modelo.")

                return False


        else:
            if 'marca' in self.filtros:
                modelos_marca = self.marcas_modelos[self.filtros['marca']]


                for modelo in modelos_marca:
                    if modelo.lower() == resposta.lower():
                        self.filtros['modelo'] = modelo
                        return True

                for modelo in modelos_marca:
                    if resposta.lower() in modelo.lower() or modelo.lower() in resposta.lower():
                        print(f"Você quis dizer {modelo}? (s/n)")
                        confirmacao = input().lower()
                        if confirmacao in ['s', 'sim', 'y', 'yes']:
                            self.filtros['modelo'] = modelo
                            return True

                modelos_disponiveis = ', '.join(modelos_marca)
                print(f"Modelo não encontrado para {self.filtros['marca']}. Modelos disponíveis: {modelos_disponiveis}")
                return False
            else:
                self.filtros['modelo'] = resposta.capitalize()
                return True



    def consultar_ano(self, resposta):

        if resposta.lower() in ['qualquer', 'tanto faz']:
            return True

        try:
            ano = int(resposta)
            if 1980 <= ano <= 2025:
                self.filtros['ano'] = ano
                return True
            else:
                print("Informe um ano entre 1980 e 2025.")
                return False
        except ValueError:
            print("Informe um ano válido (ex.: 2020).")
            return False



    def consultar_preco(self, resposta):

        if resposta.lower() in ['qualquer', 'tanto faz']:
            return True

        # REMOVE PONTO E VIRGULA PRA TRATAR MELHOR O PARSING
        resposta_limpa = resposta.replace('.', '').replace(',', '')
        numeros = re.findall(r'\d+', resposta_limpa)

        if len(numeros) >= 2:
            preco_min = float(numeros[0])
            preco_max = float(numeros[1])

            if preco_min < 1000:
                preco_min *= 1000
            if preco_max < 1000:
                preco_max *= 1000

            self.filtros['preco_min'] = preco_min
            self.filtros['preco_max'] = preco_max


        elif len(numeros) == 1:
            preco = float(numeros[0])
            if preco < 1000:
                preco *= 1000
            self.filtros['preco_max'] = preco


        else:
            print("Por favor, informe uma faixa de preço válida (ex.: '50 a 100' ou 'até 80').")
            return False

        return True



    def consultar_arCondicionado(self, resposta):

        if resposta.lower() in ['sim', 'precisa', 'quero', 'é necessário', 'obrigatório']:
            self.filtros['opcionais'] = self.filtros.get('opcionais', []) + ['Ar condicionado']
        return True



    def consultar_opcionais(self, resposta):

        if resposta.lower() not in ['nenhum', 'não', 'nao']:
            opcionais = [opc.strip().capitalize() for opc in resposta.split(',')]
            self.filtros['opcionais'] = self.filtros.get('opcionais', []) + opcionais
        return True



    def consultar_condicao(self, resposta):

        condicoes_map = {
            'novo': 'Novo',
            'seminovo': 'Seminovo',
            'semi-novo': 'Seminovo',
            'usado': 'Usado',
            'zero': 'Novo',
            '0km': 'Novo'
        }

        resposta_lower = resposta.lower()
        for key, value in condicoes_map.items():
            if key in resposta_lower:
                self.filtros['condicao'] = value
                break

        return True



    def consultar_transmissao(self, resposta):

        resposta_lower = resposta.lower()
        if any(word in resposta_lower for word in ['automático', 'automatico', 'auto']):
            self.filtros['transmissao'] = 'Automático'
        elif 'manual' in resposta_lower:
            self.filtros['transmissao'] = 'Manual'
        return True



    def consultar_cor(self, resposta):

        if resposta.lower() not in ['qualquer', 'tanto faz', 'nenhuma']:
            self.filtros['cor_evitar'] = resposta.capitalize()
        return True

    def consultar_combustivel(self, resposta):

        combustiveis_map = {
            'gasolina': 'Gasolina',
            'etanol': 'Etanol',
            'alcool': 'Etanol',
            'flex': 'Flex',
            'híbrido': 'Híbrido',
            'hibrido': 'Híbrido',
            'diesel': 'Diesel',
            'elétrico': 'Elétrico',
            'eletrico': 'Elétrico',
            'gnv': 'GNV'
        }


        resposta_lower = resposta.lower()
        for key, value in combustiveis_map.items():
            if key in resposta_lower:
                self.filtros['combustivel'] = value
                break


        return True


    def consultar_quilometragem(self, resposta):

        numeros = re.findall(r'\d+', resposta)
        if numeros:
            km = float(numeros[0])
            if km < 1000:
                km *= 1000
            self.filtros['quilometragem_max'] = km
        return True



    def exibir_resultado(self, resultados):

        if 'erro' in resultados:
            print(f"❌ Ops, ocorreu um erro: {resultados['erro']}")
            return

        if not resultados or not resultados.get('resultados'):
            print("❌ Nenhum veículo encontrado com esses filtros.")
            print("💡 Dica: Tente relaxar alguns critérios ou expandir a faixa de preço.")
            return

        veiculos = resultados['resultados']
        total = len(veiculos)

        print(f"\n🎉 Encontramos {total} veículo(s) para você:")
        print("=" * 50)

        for i, veiculo in enumerate(veiculos[:10], 1):  # Mostra até 10 resultados
            print(f"🚗 {i}. {veiculo['marca']} {veiculo['modelo']} ({veiculo['ano']})")
            print(f"   💰 Preço: R$ {veiculo['preco']:,.2f}")
            print(f"   🎨 Cor: {veiculo['cor']}")
            print(f"   📊 Quilometragem: {veiculo['quilometragem']:,} km")
            print(f"   📋 Condição: {veiculo['condicao']}")
            print(f"   📍 Localização: {veiculo['cidade']}, {veiculo['estado']}")

            if veiculo.get('opcionais'):
                print(f"   🔧 Opcionais: {', '.join(veiculo['opcionais'])}")

            quebra_linha()

        if total > 10:
            print(f"... e mais {total - 10} veículo(s).")

    def iniciar_chat(self):

        print("🚗 Olá! Sou seu assistente virtual para encontrar o carro perfeito! 😊")
        print("💬 Você pode me contar o que procura ou responder minhas perguntas.")
        print("🛑 Para parar, digite 'parar' a qualquer momento.\n")


        while True:
            try:
                user_input = input("🗣️  Me conte o que você quer num carro: ").strip()

                if user_input.lower() in ['parar', 'sair', 'fim', 'quit']:
                    print("👋 Ok, até a próxima!")
                    return

                if not user_input:
                    print("❓ Por favor, digite algo sobre o carro que você procura.")
                    continue

                # USA GEMINI:
                print("🤖 Analisando suas preferências...")
                filtros = self.gemini(user_input)


                if filtros:
                    self.atualizar_filtros(filtros)
                    print("✅ Entendi algumas preferências!")
                else:
                    print("❓ Não consegui entender completamente. Vamos fazer algumas perguntas:")


                filtros_essenciais = ['marca', 'modelo', 'preco_max']
                faltando = [f for f in filtros_essenciais if f not in self.filtros]



                if faltando:
                    print(f"\n📝 Vou fazer algumas perguntas para completar:")

                    for pergunta, processador in self.perguntas:
                        if any(f in faltando for f in filtros_essenciais):
                            while True:
                                resposta = input(f"❓ {pergunta} ").strip()

                                if resposta.lower() in ['parar', 'sair', 'fim']:
                                    print("👋 Ok, até a próxima!")
                                    return

                                if not resposta:
                                    print("❓ Por favor, digite uma resposta.")
                                    continue

                                if processador(resposta):
                                    break

                        faltando = [f for f in filtros_essenciais if f not in self.filtros]



                print("\n🔍 Filtros aplicados:")
                for chave, valor in self.filtros.items():
                    print(f"   • {chave}: {valor}")

                print("\n🔎 Buscando carros...")

                resposta = self.cliente.buscarVeiculos(self.filtros)
                self.exibir_resultado(resposta)

                nova_busca = input("\n🔄 Quer fazer uma nova busca? (s/n): ").strip().lower()
                if nova_busca not in ['s', 'sim', 'y', 'yes']:
                    print("👋 Obrigado por usar nosso serviço!")
                    break
                else:
                    self.filtros = {}
                    print("\n" + "=" * 50)



            except KeyboardInterrupt:
                print("\n👋 Programa interrompido. Até logo!")
                break
            except Exception as e:
                print(f"Erro no chat: {e}")
                print(f"❌ Ocorreu um erro: {e}")
                print("🔄 Vamos tentar novamente...")



# RUN
if __name__ == "__main__":
    agente = AgenteVirtual()
    agente.iniciar_chat()